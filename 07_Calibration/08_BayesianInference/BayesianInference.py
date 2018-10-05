import pandas as pd
import numpy as np
from scipy.stats import norm
from globalSetting import globalParameters

# import global parameter setting
gParameter = globalParameters()
trainingYrs = gParameter.trainingYears
threshold = gParameter.threshold
conn = gParameter.conn
p_Tmin = gParameter.p_Tmin
p_Ninf = gParameter.p_Ninf


# The function checks if the PC6 measured energy data falls withing the PC6 simulation ranges
def detectOutlier(df, threshold, remove=True):
    outlierIDs = []
    for i in range(len(df)):
        pc6consumption = df.iloc[i, 3]
        simMax = max(df.iloc[i, 4:]) + threshold
        simMin = min(df.iloc[i, 4:]) - threshold
        if not simMin <= pc6consumption <= simMax:
            outlierIDs.append(i)
    if bool(remove):
        df.drop(outlierIDs, inplace=True)
        cleaned_df = df.reset_index(drop=True).iloc[:,1:]
    return cleaned_df


# Count and collect the training years of each postcode
def trainingCounts(cleaned_df, trainingPC6counts, simulationYear):
    pc6IDs = cleaned_df.iloc[:,0]
    for pc6 in pc6IDs:
        if bool(trainingPC6counts.get(pc6)):
            trained_yrs = trainingPC6counts[pc6]
            trained_yrs.append(simulationYear)
            trainingPC6counts[pc6] = trained_yrs
        else:
            trainingPC6counts[pc6] = [simulationYear]
    return trainingPC6counts


def dinstinctArchetype(cleaned_df):
    archetypes = cleaned_df.archetype.unique()
    return archetypes


def getArchetypeIDs(cleaned_df, archetype):
    archIDs = cleaned_df.index[cleaned_df['archetype'] == archetype].tolist()
    return archIDs


def getArchtypeStatistics(cleaned_df, archetype):
    archIDs = getArchetypeIDs(cleaned_df, archetype)
    archMu = np.mean(cleaned_df.loc[archIDs, 'l_pc6_consumption_kwh_m3'])
    archStd = np.std(cleaned_df.loc[archIDs, 'l_pc6_consumption_kwh_m3'])
    return archMu, archStd


def computelikelihood(meteredConsumption, nSimConsumption, archStd):
    likelihood = norm.pdf(meteredConsumption, nSimConsumption, archStd)
    return likelihood


def computePosterior(cleaned_df, pc6_name, pc6_metered, archetype, prior, gridSize):
    archMu, archStd = getArchtypeStatistics(cleaned_df, archetype)
    # In case the specific archetype has only one record e.g. SHF type, assigning 5.0 as an archetype std
    # It is found many archStd ranges are too broad, so the posterior might be indistinguishable in some cases,
    # in such case, archStd is divided by 5.0
    if archStd <= 1.0:
        archStd = 5.0
    else:
        archStd = archStd/5.0

    likelihoodXprior = []
    pc6_id = cleaned_df.index[cleaned_df['postcode'] == pc6_name]

    for n in range(gridSize * gridSize):
        nSimConsumption = cleaned_df.loc[pc6_id, 'case' + str(n + 1) + '_kwh_m3']
        nLikelihood = computelikelihood(pc6_metered, nSimConsumption, archStd)
        # likelihoodXprior.append(nLikelihood*prior[n])
        # to avoid numerical problem, apply the principle: log(product(Pi))=sum(log(Pi))
        likelihoodXprior.append(np.log(nLikelihood) + np.log(prior[n]))

    likelihoodXprior = np.exp(likelihoodXprior)
    probD = sum(likelihoodXprior)
    pc6_posterior = np.multiply(likelihoodXprior, 100.0) / probD
    return pc6_posterior


def trainingPhase():
    gridSize = globalParameters().gridSize
    # initialize an empty dict() to record trained year count of each postcode
    trainingPC6counts = dict()
    # initialize an empty dict() to update prior to posterior during the training phase
    pc6_prob = dict()
    pc6_archetype = dict()

    for year in trainingYrs:
        # pre-processing input data
        path = gParameter.fileDirectory + gParameter.filePrefix + str(year) + '.csv'
        df = pd.read_csv(path, delimiter=',', index_col=False)
        cleaned_df = detectOutlier(df, threshold, remove=True)

        # recording each PC6 has gone through how many years of training
        pc6TrainedCounts = trainingCounts(cleaned_df, trainingPC6counts, year)

        for pc6, archetype, pc6_metered in zip(cleaned_df.iloc[:, 0], cleaned_df.iloc[:, 1], cleaned_df.iloc[:, 2]):
            # if this is the first time the pc6 is trained, initialize equal prior probability,
            if pc6_prob.get(pc6) is None:
                pc6_prob[pc6] = [(1.0 / gridSize) ** 2] * (gridSize * gridSize)
                pc6_archetype[pc6] = archetype

            # compute posterior for each postcode of the year, and update the prior with posterior
            prior = pc6_prob[pc6]
            posterior = computePosterior(cleaned_df, pc6, pc6_metered, archetype, prior, gridSize)
            pc6_prob[pc6] = posterior

    return pc6_prob, pc6TrainedCounts, pc6_archetype


def inputCombination(p_Tmin, p_Ninf):
    inputSets = []
    for p_temp in p_Tmin:
        for p_inf in p_Ninf:
            inputSets.append([p_temp, p_inf])
    return inputSets


def createPC6_posteriorInputsDB(conn):
    cur = conn.cursor()
    cur.execute(
        """
        DROP TABLE IF EXISTS public."pc6_posterior_results";

        CREATE TABLE public."pc6_posterior_results"
        (
        "postcode" character varying,
        "archetype" character varying,
        "maxProb" DOUBLE PRECISION ,
        "post_Tmin" DOUBLE PRECISION,
        "post_Ninf" DOUBLE PRECISION,
        "trainingTimes" integer
        );
        """
    )
    cur.close()
    conn.commit()


# pick up the most likely input combination from the joint posterior distribution
def pickUpInputCombination(pc6_prob, pc6TrainedCounts, pc6_archetype, inputSets, conn):
    # create or overwrite a table in DB to store calibrated information
    createPC6_posteriorInputsDB(conn)

    cur = conn.cursor()
    for pc6 in pc6_prob.keys():
        archetype = pc6_archetype[pc6]
        maxProb = max(pc6_prob[pc6].tolist())[0]
        maxProbID = pc6_prob[pc6].tolist().index(max(pc6_prob[pc6].tolist()))
        post_Tmin = inputSets[maxProbID][0]
        post_Ninf = inputSets[maxProbID][1]
        trainingTimes = len(pc6TrainedCounts[pc6])

        cur.execute(
        """INSERT INTO public."pc6_posterior_results"
           VALUES (%s, %s, %s, %s, %s, %s)""", [pc6, archetype, maxProb, post_Tmin, post_Ninf, trainingTimes]
        )
    cur.close()
    conn.commit()


def main():
    pc6_prob, pc6TrainedCounts, pc6_archetype = trainingPhase()

    inputSets = inputCombination(p_Tmin, p_Ninf)
    pickUpInputCombination(pc6_prob, pc6TrainedCounts, pc6_archetype, inputSets, conn)


if __name__ == '__main__':
    main()
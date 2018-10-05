# Following the instruction to execute the scripts in sequence to perform validation simulation and analysis

1. Always starts with checking the globalSetting to see if the validation year, type (baseline or calibrated?) is correct or not

2. "populateBaselineInputs" and "populatePosteriorInputs" will create tables and insert baseline, carlibrated model inputs into the tables in DB.

3. "populateXMLConstruction" is used to add construction data into the CitySim.xml files, it is excuted automatically when running a "XML_...Updater_AMSmodels" script

4. When semantic updated CitySim.xml is ready, "runCitySim_Validation" can be executed, make sure the CitySim fileName, simulation type and year are correct.

5. "resultCleaning" will normalize Liander gas consumption (m3/yr) and simulation result (W/yr) into Energy Use Intensity unit: (kWh/m3.yr)

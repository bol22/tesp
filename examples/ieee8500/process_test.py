#	Copyright (C) 2017 Battelle Memorial Institute
# file: process_gld.py; custom for the IEEE 8500-node circuit
import json;
import sys;
import numpy as np;
import matplotlib as mpl;
import matplotlib.pyplot as plt;

# first, read and print a dictionary of all the monitored GridLAB-D objects
lp = open (sys.argv[1] + "_glm_dict.json").read()
dict = json.loads(lp)
sub_keys = list(dict['feeders'].keys())
sub_keys.sort()
inv_keys = list(dict['inverters'].keys())
inv_keys.sort()
hse_keys = list(dict['houses'].keys())
hse_keys.sort()
mtr_keys = list(dict['billingmeters'].keys())
mtr_keys.sort()
cap_keys = list(dict['capacitors'].keys())
cap_keys.sort()
reg_keys = list(dict['regulators'].keys())
reg_keys.sort()
xfMVA = dict['transformer_MVA']
matBus = dict['matpower_id']
print ("\n\nFile", sys.argv[1], "has substation", sub_keys[0], "at Matpower bus", matBus, "with", xfMVA, "MVA transformer")
print("\nFeeder Dictionary:")
for key in sub_keys:
	row = dict['feeders'][key]
#	print (key, "has", row['house_count'], "houses and", row['inverter_count'], "inverters")
print("\nBilling Meter Dictionary:")
for key in mtr_keys:
	row = dict['billingmeters'][key]
#	print (key, "on phase", row['phases'], "of", row['feeder_id'], "with", row['children'])
print("\nHouse Dictionary:")
for key in hse_keys:
	row = dict['houses'][key]
#	print (key, "on", row['billingmeter_id'], "has", row['sqft'], "sqft", row['cooling'], "cooling", row['heating'], "heating", row['wh_gallons'], "gal WH")
	# row['feeder_id'] is also available
print("\nInverter Dictionary:")
for key in inv_keys:
	row = dict['inverters'][key]
#	print (key, "on", row['billingmeter_id'], "has", row['rated_W'], "W", row['resource'], "resource")
	# row['feeder_id'] is also available

# parse the substation metrics file first; there should just be one entity per time sample
# each metrics file should have matching time points
lp_s = open ("substation_" + sys.argv[1] + "_metrics.json").read()
lst_s = json.loads(lp_s)
print ("\nMetrics data starting", lst_s['StartTime'])

# make a sorted list of the sample times in hours
lst_s.pop('StartTime')
meta_s = lst_s.pop('Metadata')
times = list(map(int,list(lst_s.keys())))
times.sort()
print ("There are", len (times), "sample times at", times[1] - times[0], "second intervals")
hrs = np.array(times, dtype=np.float)
denom = 3600.0
hrs /= denom

# parse the substation metadata for 2 things of specific interest
print ("\nSubstation Metadata for", len(lst_s['3600']), "objects")
for key, val in meta_s.items():
#	print (key, val['index'], val['units'])
	if key == 'real_power_avg':
		SUB_POWER_IDX = val['index']
		SUB_POWER_UNITS = val['units']
	elif key == 'real_power_losses_avg':
		SUB_LOSSES_IDX = val['index']
		SUB_LOSSES_UNITS = val['units']

# create a NumPy array of all metrics for the substation
data_s = np.empty(shape=(len(sub_keys), len(times), len(lst_s['3600'][sub_keys[0]])), dtype=np.float)
print ("\nConstructed", data_s.shape, "NumPy array for Substations")
j = 0
for key in sub_keys:
	i = 0
	for t in times:
		ary = lst_s[str(t)][sub_keys[j]]
		data_s[j, i,:] = ary
		i = i + 1
	j = j + 1

# display some averages
print ("Maximum power =", data_s[0,:,SUB_POWER_IDX].max(), SUB_POWER_UNITS)
print ("Average power =", data_s[0,:,SUB_POWER_IDX].mean(), SUB_POWER_UNITS)
print ("Average losses =", data_s[0,:,SUB_LOSSES_IDX].mean(), SUB_LOSSES_UNITS)

# read the other JSON files; their times (hrs) should be the same
lp_h = open ("house_" + sys.argv[1] + "_metrics.json").read()
lst_h = json.loads(lp_h)
lp_m = open ("billing_meter_" + sys.argv[1] + "_metrics.json").read()
lst_m = json.loads(lp_m)
lp_i = open ("inverter_" + sys.argv[1] + "_metrics.json").read()
lst_i = json.loads(lp_i)
lp_c = open ("capacitor_" + sys.argv[1] + "_metrics.json").read()
lst_c = json.loads(lp_c)
lp_r = open ("regulator_" + sys.argv[1] + "_metrics.json").read()
lst_r = json.loads(lp_r)

# houses
lst_h.pop('StartTime')
meta_h = lst_h.pop('Metadata')
print("\nHouse Metadata for", len(lst_h['3600']), "objects")
for key, val in meta_h.items():
#	print (key, val['index'], val['units'])
	if key == 'air_temperature_max':
		HSE_AIR_MAX_IDX = val['index']
		HSE_AIR_MAX_UNITS = val['units']
	elif key == 'air_temperature_min':
		HSE_AIR_MIN_IDX = val['index']
		HSE_AIR_MIN_UNITS = val['units']
	elif key == 'air_temperature_avg':
		HSE_AIR_AVG_IDX = val['index']
		HSE_AIR_AVG_UNITS = val['units']
	elif key == 'air_temperature_median':
		HSE_AIR_MED_IDX = val['index']
		HSE_AIR_MED_UNITS = val['units']
	elif key == 'total_load_avg':
		HSE_TOTAL_AVG_IDX = val['index']
		HSE_TOTAL_AVG_UNITS = val['units']
	elif key == 'hvac_load_avg':
		HSE_HVAC_AVG_IDX = val['index']
		HSE_HVAC_AVG_UNITS = val['units']
	elif key == 'waterheater_load_avg':
		HSE_WH_AVG_IDX = val['index']
		HSE_WH_AVG_UNITS = val['units']
data_h = np.empty(shape=(len(hse_keys), len(times), len(lst_h['3600'][hse_keys[0]])), dtype=np.float)
print ("\nConstructed", data_h.shape, "NumPy array for Houses")
j = 0
for key in hse_keys:
	i = 0
	for t in times:
		ary = lst_h[str(t)][hse_keys[j]]
		data_h[j, i,:] = ary
		i = i + 1
	j = j + 1

print ('average all house temperatures during simulation:', data_h[:,:,HSE_AIR_AVG_IDX].mean())

# Billing Meters 
lst_m.pop('StartTime')
meta_m = lst_m.pop('Metadata')
print("\nBilling Meter Metadata for", len(lst_m['3600']), "objects")
for key, val in meta_m.items():
#	print (key, val['index'], val['units'])
	if key == 'voltage_max':
		MTR_VOLT_MAX_IDX = val['index']
		MTR_VOLT_MAX_UNITS = val['units']
	elif key == 'voltage_min':
		MTR_VOLT_MIN_IDX = val['index']
		MTR_VOLT_MIN_UNITS = val['units']
	elif key == 'voltage_avg':
		MTR_VOLT_AVG_IDX = val['index']
		MTR_VOLT_AVG_UNITS = val['units']
	elif key == 'voltage12_max':
		MTR_VOLT12_MAX_IDX = val['index']
		MTR_VOLT12_MAX_UNITS = val['units']
	elif key == 'voltage12_min':
		MTR_VOLT12_MIN_IDX = val['index']
		MTR_VOLT12_MIN_UNITS = val['units']
	elif key == 'voltage_unbalance_max':
		MTR_VOLTUNB_MAX_IDX = val['index']
		MTR_VOLTUNB_MAX_UNITS = val['units']

data_m = np.empty(shape=(len(mtr_keys), len(times), len(lst_m['3600'][mtr_keys[0]])), dtype=np.float)
print ("\nConstructed", data_m.shape, "NumPy array for Meters")
j = 0
for key in mtr_keys:
	i = 0
	for t in times:
		ary = lst_m[str(t)][mtr_keys[j]]
		data_m[j, i,:] = ary
		i = i + 1
	j = j + 1

lst_i.pop('StartTime')
meta_i = lst_i.pop('Metadata')
print("\nInverter Metadata for", len(lst_i['3600']), "objects")
for key, val in meta_i.items():
#	print (key, val['index'], val['units'])
	if key == 'real_power_avg':
		INV_P_AVG_IDX = val['index']
		INV_P_AVG_UNITS = val['units']
	elif key == 'reactive_power_avg':
		INV_Q_AVG_IDX = val['index']
		INV_Q_AVG_UNITS = val['units']
data_i = np.empty(shape=(len(inv_keys), len(times), len(lst_i['3600'][inv_keys[0]])), dtype=np.float)
print ("\nConstructed", data_i.shape, "NumPy array for Inverters")
j = 0
for key in inv_keys:
	i = 0
	for t in times:
		ary = lst_i[str(t)][inv_keys[j]]
		data_i[j, i,:] = ary
		i = i + 1
	j = j + 1

lst_c.pop('StartTime')
meta_c = lst_c.pop('Metadata')
print("\nCapacitor Metadata for", len(lst_c['3600']), "objects")
for key, val in meta_c.items():
	if key == 'operation_count':
		CAP_COUNT_IDX = val['index']
		CAP_COUNT_UNITS = val['units']
data_c = np.empty(shape=(len(cap_keys), len(times), len(lst_c['3600'][cap_keys[0]])), dtype=np.float)
print ("\nConstructed", data_c.shape, "NumPy array for Capacitors")
j = 0
for key in cap_keys:
	i = 0
	for t in times:
		ary = lst_c[str(t)][cap_keys[j]]
		data_c[j, i,:] = ary
		i = i + 1
	j = j + 1

lst_r.pop('StartTime')
meta_r = lst_r.pop('Metadata')
print("\nRegulator Metadata for", len(lst_c['3600']), "objects")
for key, val in meta_r.items():
	if key == 'operation_count':
		REG_COUNT_IDX = val['index']
		REG_COUNT_UNITS = val['units']
data_r = np.empty(shape=(len(reg_keys), len(times), len(lst_r['3600'][reg_keys[0]])), dtype=np.float)
print ("\nConstructed", data_r.shape, "NumPy array for Regulators")
j = 0
for key in reg_keys:
	i = 0
	for t in times:
		ary = lst_r[str(t)][reg_keys[j]]
		data_r[j, i,:] = ary
		i = i + 1
	j = j + 1

# assemble the total solar and battery inverter power
j = 0
solar_kw = np.zeros(len(times), dtype=np.float)
battery_kw = np.zeros(len(times), dtype=np.float)
for key in inv_keys:
	res = dict['inverters'][key]['resource']
	if res == 'solar':
		solar_kw += 0.001 * data_i[j,:,INV_P_AVG_IDX]
	elif res == 'battery':
		battery_kw += 0.001 * data_i[j,:,INV_P_AVG_IDX]
	j = j + 1

# display a plot
fig, ax = plt.subplots(1, 3, sharex = 'col')

ax[0].plot(hrs, data_h[0,:,HSE_AIR_AVG_IDX], color="blue", label="Mean")
ax[0].plot(hrs, data_h[0,:,HSE_AIR_MIN_IDX], color="red", label="Min")
ax[0].plot(hrs, data_h[0,:,HSE_AIR_MAX_IDX], color="green", label="Max")
ax[0].plot(hrs, data_h[0,:,HSE_AIR_MED_IDX], color="magenta", label="Median")
ax[0].set_xlabel("Hours")
ax[0].set_ylabel(HSE_AIR_AVG_UNITS)
ax[0].set_title ("House Air at " + hse_keys[0])
ax[0].legend(loc='best')

ax[1].plot(hrs, solar_kw, color="blue")
ax[1].set_xlabel("Hours")
ax[1].set_ylabel("kW")
ax[1].set_title ("Total Solar Power")

ax[2].plot(hrs, battery_kw, color="blue")
ax[2].set_xlabel("Hours")
ax[2].set_ylabel("kW")
ax[2].set_title ("Total Battery Power")

plt.show()



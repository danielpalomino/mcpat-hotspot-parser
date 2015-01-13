import re
import sys

#regular expressions
ncores = re.compile('Total Cores: (\d+) cores')
nl2s = re.compile('Total L2s: (\d+)')

re_core = 'Core:\n'
re_l2 = 'L2\n'
re_area = '\s*Area\s*=\s*([0-9.]*)\s*\w*\^\w*\n'
re_peak = '\s*Peak\s*Dynamic\s*=\s*([0-9.]*)\s*\w*\n'
re_subth = '\s*Subthreshold\s*Leakage\s*=\s*([0-9.]*)\s*\w*\n'
re_gate = '\s*Gate\s*Leakage\s*=\s*([0-9.]*)\s*\w*\n'
re_run = '\s*Runtime\s*Dynamic\s*=\s*([0-9.]*)\s*\w*\n'

core = re.compile(re_core+re_area+re_peak+re_subth+re_gate+re_run)
l2 = re.compile(re_l2+re_area+re_peak+re_subth+re_gate+re_run)

#OFFSET TO MULTPLY THE POWER TRACES TO INCREASE TEMPERATURE FASTER
OFFSET = 1.5
#FACTOR TO INCREASE THE NUMBER OF TRACES (INCREASE SIMULATION)
N_INC = 3

#READ ALL LINES OF FILE
def get_lines_of_file(fin):
	all_lines = fin.read()
	fin.close()
	return all_lines

#GET NUMBER OF ELEMENTS BASED ON DE "elem" re object.
#elem = regular expression object for number of elements (core, l2, etc...)
#all_lines = the file
def get_number_of_elems(elem, all_lines):
	m = elem.search(all_lines)
	if m:
		return int(m.group(1))
	else:
		return 1

#GET LIST OF POWER TRACES. THE LIST CONTAINS LISTS OF POWER TRACES FOR ALL ELEMENTS OF THE SAME TYPE (ex: core0, core1, ..., coren)
#elem = regular expression object for attributes of element "elem"
def get_power_traces(elem, number_of_elems, all_lines):
	p_traces = []
	for n in range(0,number_of_elems):
		p_traces.append([])
		
	traces_list = elem.findall(all_lines)
	for i in range(0,len(traces_list)):
		p_traces[i%number_of_elems].append(traces_list[i][4]);
	return p_traces

#WRITE HEADER TO PTRACE FILE (ONLY CORES AND L2S FOR NOW)
def write_header_ptrace(fout,number_of_cores,number_of_l2s):
	#WRITE CORES HEADERS
	for i in range(0,number_of_cores):
		fout.write('Core_'+str(i)+'\t')
	#WRITE L2s HEADERS
	for i in range(0,number_of_l2s):
		fout.write('L2_'+str(i)+'\t')
	#WRITE NEW LINE
	fout.write('\n')

#WRITE POWER TRACES TO PTRACE FILE (ONLY CORES AND L2S FOR NOW)
def write_traces_ptrace(fout,number_of_traces,p_traces_cores,p_traces_l2s):
	for i in range(0,number_of_traces):
		#write cores traces
		for j in range(0,len(p_traces_cores)):
			fout.write(str(float(p_traces_cores[j][i])*OFFSET) + '\t')
		#write l2s traces
		for j in range(0,len(p_traces_l2s)):
			fout.write(p_traces_l2s[j][i] + '\t')	
#		for j in range(0,len(p_traces_l2s)):
#			fout.write(p_traces_l2s[j][i] + '\t')	
		fout.write('\n')

#n_increase = number of times that the traces will be increased
def artificial_sim_increase(p_traces,number_of_traces,n_increase):
	for i in range(0,n_increase):
		for j in range(0,len(p_traces)):
			last_trace = p_traces[j][-1]
			#increase traces
			for k in range(0,number_of_traces):
				p_traces[j].append(str(float(p_traces[j][k])+float(last_trace)))

all_p_traces_cores = []

last_parameter = sys.argv[-1]
if last_parameter.split('.')[-1] != 'ptrace':
    raise ValueError('DANIEL ERROR(0): Last parameter should be a ptrace extension file')
else:

    #READ ALL INPUT MCPAT LOG FILES AND GET THE CORES TRACES TOGETHER (ONLY THE CORES EXCITED BY THE SIMULATION (CORE_O))
    for i in range(1,len(sys.argv)-1):
	fin = open(sys.argv[i],'r')

	all_lines = get_lines_of_file(fin)

	number_of_cores = get_number_of_elems(ncores,all_lines)

	number_of_l2s = get_number_of_elems(nl2s,all_lines)
	
	p_traces_cores = get_power_traces(core,number_of_cores,all_lines)

	p_traces_l2s = get_power_traces(l2,number_of_l2s,all_lines)

	all_p_traces_cores.append(p_traces_cores[0])

    artificial_sim_increase(all_p_traces_cores,len(all_p_traces_cores[0]),N_INC)
    artificial_sim_increase(p_traces_l2s,len(p_traces_l2s[0]),N_INC)

    #CALCULATE NUMBER OF TRACES TO BE PRINTED IN CASE OF FILES DIFFER (get smaller)
    number_of_traces = len(all_p_traces_cores[0])
    for p_traces_cores in all_p_traces_cores:
	if len(p_traces_cores) < number_of_traces:
		number_of_traces = len(p_traces_cores)


    fout = open(sys.argv[-1],'w')

    #WRITE HEADER TO PTRACE FILE
    #last parameter is the number of l2s. In case of 8 cores I have been using 2 l2s
    write_header_ptrace(fout,len(all_p_traces_cores),1)

    #WRITE POWER TRACES
    write_traces_ptrace(fout,number_of_traces,all_p_traces_cores,p_traces_l2s)

    fout.close()




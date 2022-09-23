import os
import shutil
import subprocess

def assignVariables(file_path, variables, values):
    """
    Assigns a variable to a value.
    """
    # Read in the file
    with open('templates/hexagon.in', 'r') as f:
        filedata = f.read()

    # Replace the target string
    for i in range(len(variables)):
        filedata = filedata.replace(variables[i], str(values[i]))

    # Write the file out again
    if not os.path.exists(file_path):
        os.makedirs(file_path)

    with open(f'{file_path}/hexagon-{seed}.in', 'w') as f:
        f.write(filedata)

    # Copy body file
    shutil.copyfile('templates/hex.conf', f'{file_path}/hex.conf')

    # Copy the SLURM script
    with open('templates/run.sh', 'r') as f:
        filedata = f.read()
    filedata = filedata.replace('$SEED', str(seed))
    with open(f'{file_path}/run-{seed}.sh', 'w') as f:
        f.write(filedata)



# run main
if __name__ == '__main__':

    folder_name = 'single_temp_small'

    if not os.path.exists(f'../dataset/{folder_name}'):
        os.makedirs(f'../dataset/{folder_name}')

    variables = ['$R_IN', '$R_CUT', '$TEMP', '$R0', '$K', '$SEED', '$LOG_FREQ', '$RUNSTEPS', '$TIMESTEP' ]
    
    R_cut = 2 ** (1/6)
    R_in = R_cut - R_cut * 0.05
    temp = 2.5
    r0 = 2
    k = 10*temp/R_in/R_in
    
    # takes about 50 seconds
    log_freq = 100000
    runsteps = 100000000
    timestep = 0.00001
    
    train_split = 0.8
    test_split = 0.1
    validate_split = 0.1
    assert train_split + test_split + validate_split == 1

    num_of_sims = 20
    train_n = int(num_of_sims * train_split)
    test_n = int(num_of_sims * test_split)
    validate_n = int(num_of_sims * validate_split)
    assert train_n + test_n + validate_n == num_of_sims

    # Create script to run all
    run_script = []

    # with open('templates/run.sh', 'w') as slurm_file:
    #     slurm_file = slurm_file.readlines()
    #     slurm_file.append('\n')



    # train
    for seed in range(1, train_n + 1):
        values = [R_in, R_cut, temp, r0, k, seed, log_freq, runsteps, timestep]
        assignVariables(f'../dataset/{folder_name}/train', variables, values)
        run_script += [f'cd train/ \n', f'sbatch run-{seed}.sh \n', 'cd .. \n']
        
        
    # test
    for seed in range(train_n + 1, (train_n + 1) + test_n):
        values = [R_in, R_cut, temp, r0, k, seed, log_freq, runsteps, timestep]
        assignVariables(f'../dataset/{folder_name}/test', variables, values)
        run_script += [f'cd test/ \n', f'sbatch run-{seed}.sh \n', 'cd .. \n']
        

    # validate
    for seed in range((train_n + 1) + test_n, ((train_n + 1) + test_n) + validate_n):
        values = [R_in, R_cut, temp, r0, k, seed, log_freq, runsteps, timestep]
        assignVariables(f'../dataset/{folder_name}/validation', variables, values)
        run_script += [f'cd validation/ \n', f'sbatch run-{seed}.sh \n', 'cd .. \n']
        
    with open(f'../dataset/{folder_name}/run.sh', 'w') as f:
        f.writelines(run_script)
            
    # run slurm script
    os.chdir(f'../dataset/{folder_name}/')
    subprocess.call(['sh', 'run.sh'])

    # TODO: make it so that the produced datasets are in the correct folders in dataset/
    # TODO: run LAMMPS from python

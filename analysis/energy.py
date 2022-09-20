import torch
import pandas as pd
import sys
import os
import numpy as np
sys.path.insert(0, os.path.abspath('..'))
from diffmd.training import Trainer

natoms = 14

config = dict(
    folder = '../dataset/single_temp_large_cut_strong_spring',
    # folder = '../dataset/single_temp_small',
    device = torch.device('cpu'), 
    training_fraction=1.0,
    random_dataset=False,
    traj_step=1,
    epochs = 100,
    start_epoch = 0,
    optimizer = 'Adamax',
    weight_decay=0,
    batch_length=20,
    batch_length_step=10,
    batch_length_freq=100,
    batch_size=10000,
    shuffle=True,
    num_workers=0,
    learning_rate=0.02,
    nn_widths=[64, 48, 32],
    activation_function='tanh',
    eval_batch_length=1,
    eval_init_skip=1,
    eval_traj_step=1,
    load_folder='../results/2022-09-19/19-17-43',
    dtype=torch.float32,
    itr_printing_freq=1,
    printing_freq=1,
    plotting_freq=6000,
    stopping_freq=6000,
    stopping_look_back=2,
    scheduler=None,
    scheduling_factor=0.5,
    scheduling_freq=25,
    evaluation_freq=5,
    checkpoint_freq=2,
    loss_func = 'final-mse-pos',
    normalize_loss = False,
    sigopt=False,
    )

if __name__ == '__main__':
    trainer = Trainer(config)

    trajectory_index = 0
    df = pd.read_csv(trainer.training_dataset.trajs[trajectory_index].file_path+'.csv')
    data = trainer.training_dataset.trajs[trajectory_index].traj
    data = [i.squeeze() for i in data]
    v, w, x, q = data
    potential = trainer.func.net

    energies = df['potential_energy'].to_numpy()
    
    # batch_length = 5000
    # trainer.training_dataset.update(batch_length, traj_step=10)
        
    # with torch.no_grad():
    #     # get the earliest init conditions to ensure trajectories are long enough
    #     batch_input, batch_y, _ = trainer.training_dataset[0]
    #     batch_input = list(batch_input)
    #     batch_input[0] = batch_input[0].unsqueeze(0)
    #     batch_input = tuple(batch_input)

    #     pred_y = trainer.forward_pass(batch_input, batch_length=batch_length).squeeze()
    #     batch_y = batch_y.cpu().numpy()
    #     batch_t = trainer.get_batch_t(batch_input[1], batch_length=batch_length).cpu().numpy())

    r = x[:, 1, :] - x[:, 0, :]
    rq = torch.cat((r, q.reshape(-1, 8)), dim=1).reshape(-1, 11).type(torch.float32)
    
    predicted_energies = potential(rq).detach().cpu().numpy()
    
    indices = np.random.randint(1000, size=rq.shape[0])

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.plot(energies[indices], predicted_energies[indices], 'bo')
    ax.plot([-4, 4], [-4, 4], 'k-')
    ax.set_xlabel('Actual')
    ax.set_ylabel('Predicted')
    # set equal aspect ratio
    ax.set_aspect('equal')
    ax.set_xlim([-4, 4])
    ax.set_ylim([-4, 4])
    fig.savefig('energy_matrix.png')
    plt.close(fig)


    num_steps = 500


    V_diff = np.diff(energies[:num_steps] * natoms)
    r_diff = np.diff(torch.norm(x[:num_steps, 0, :], dim=-1).numpy())
    actual_force = - V_diff / r_diff

    plt.plot(actual_force, 'k', label='Actual')

    plt.savefig('force_compare.png')
    plt.close()



    print('before actual')
    plt.plot(energies[:num_steps] * natoms, 'k', label='Actual')
    # plt.plot(predicted_energies[:num_steps] - predicted_energies[0], 'r', label='Predicted')
    plt.plot(predicted_energies[:num_steps], 'r', label='Predicted')


    plt.ylabel('Energy')
    plt.xlabel('Time step')
    plt.legend()
    plt.savefig('potential_compare.png')
    plt.close()

    k = trainer.training_dataset.trajs[trajectory_index].k
    r0 = trainer.training_dataset.trajs[trajectory_index].r0
    harmonic_energy = (0.5 * k * torch.square(torch.norm(r, dim=1) - r0)).detach().cpu().numpy()
    # plt.plot(energies[:num_steps] + harmonic_energy[:num_steps], 'k--', alpha=0.5, label='Actual + Harmonic')

    print('before predicted')
    plt.plot(predicted_energies[:num_steps], 'r', alpha=0.5, label='Potential')
    plt.plot(predicted_energies[:num_steps].squeeze() + harmonic_energy[:num_steps].squeeze(), 'r', alpha=1.0, label='Potential + Harmonic')
    plt.plot(harmonic_energy[:num_steps], 'r--', alpha=0.5, label='Harmonic')

    M = 7.0

    kinetic_energy_trans = torch.sum(torch.sum(0.5 * M * v**2, dim=-1), dim=-1)
    
    batch_input, _, _ = trainer.training_dataset[0]
    inertia = batch_input[-1]

    kinetic_energy_rot = torch.sum(torch.sum(0.5 * inertia * w**2, dim=-1), dim=-1)
    
    kinetic_energy = (kinetic_energy_trans + kinetic_energy_rot).detach().cpu().numpy()

    plt.plot(kinetic_energy[:num_steps], 'b-', label='Kinetic')

    total_energy = predicted_energies[:num_steps].squeeze() + harmonic_energy[:num_steps] + kinetic_energy[:num_steps]

    print('before total')
    plt.plot(total_energy, 'k--', alpha=0.8, label='Total Predicted Energy')
    
    plt.legend()
    plt.savefig('energy.png')
    plt.close()




    
    # actual_kinetic_energies = df['kinetic_energy'].to_numpy() * natoms
    # plt.plot(actual_kinetic_energies[:num_steps], 'r--', alpha=0.5, label='Actual Kinetic Energy')

    # predicted_kinetic_energies = kinetic_energy
    # plt.plot(predicted_kinetic_energies[:num_steps], 'r', alpha=1.0, label='Predicted Kinetic Energy')
    # plt.plot(kinetic_energy_trans.detach().cpu().numpy()[:num_steps], 'b', alpha=0.5, label='Predicted Trans Kinetic')
    # plt.plot(kinetic_energy_rot.detach().cpu().numpy()[:num_steps], 'g', alpha=0.5, label='Predicted Rot Kinetic')

    actual_potential_energies = df['potential_energy'].to_numpy() * natoms
    plt.plot(actual_potential_energies[:num_steps], 'b', label='Actual Potential Energy')

    # actual_total_energies = df['total_energy'].to_numpy() * natoms
    # plt.plot(actual_total_energies[:num_steps], 'k--', label='Actual Total Energy')

    plt.legend()
    plt.savefig('actual_energy.png')
    plt.close()




    # ENERGIES FROM LAMMPS
    plt.title('Logged Energies from LAMMPS')
    plt.plot(df['total_energy'].to_numpy()[:num_steps] * natoms + harmonic_energy[:num_steps], 'k', label='Total')
    plt.plot(df['potential_energy'].to_numpy()[:num_steps] * natoms, 'b', label='Potential')
    plt.plot(df['kinetic_energy'].to_numpy()[:num_steps] * natoms, 'r', label='Kinetic')
    plt.plot(harmonic_energy[:num_steps], 'g', label='Harmonic')
    plt.legend()
    plt.xlabel('Time step')
    plt.ylabel('Energy')
    plt.savefig('LAMMPS_energy.png')
    plt.close()


    # trainer.plot_traj()
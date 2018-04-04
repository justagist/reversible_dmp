import os
import numpy as np
import matplotlib.pyplot as plt
from reversible_dmp import ReversibleDMP
from config import reversible_dmp_config
from JustaPython.MouseUtils import MouseTracker


def plot_traj(trajectories):
    plt.figure("trajectories")
    
    for i in range(len(trajectories)):
        trajectory = trajectories[i]
        idx = trajectory.shape[1]*100 + 11
        if i == 0:
            color = 'r--'
        elif i==1:
            color = 'g'
        else:
            color = 'b'
        for k in range(trajectory.shape[1]):
            plt.subplot(idx)
            idx += 1
            plt.plot(trajectory[:,k], color)
    plt.show() 

def plot_path(trajectory, true_points, custom_start = None, custom_goal = None):

    
    # ----- interactive mode on
    plt.ion()

    # ----- position trajectory for plotting
    pos_trajectory = trajectory['pos_traj']

    plt.scatter(true_points[:,0],true_points[:,1], label = "Original Path", color = 'y')

    if custom_start is not None:
        plt.scatter(custom_start[0], custom_start[1], label = "Custom start", color = 'r')

    if custom_goal is not None:
        plt.scatter(custom_goal[0], custom_goal[1], label = "Custom goal", color = 'g')

    plt.axes().set_aspect('equal', 'datalim')

    i = 0

    # ----- find the resultant velocity for updating the graph at the scaled speed
    vel_square = np.square(trajectory['vel_traj'])
    resultant_vel = np.sqrt(vel_square[:,0]+vel_square[:,1])*1000

    skip_step = int(0.01*pos_trajectory.shape[0]) # ----- steps to skip so that plot update is not too slow

    while i < (pos_trajectory.shape[0]):
        try:
            plt.plot(pos_trajectory[:i,0],pos_trajectory[:i,1], label = "New path", color = 'b')

            pause = 0.001/resultant_vel[i] if resultant_vel[i] > 0.01 else 0.0001/0.01
            plt.pause(pause)
            plt.draw()

            if i < 1:
                plt.legend()

            i += skip_step

        except KeyboardInterrupt:
            break


def train_dmp(trajectory):
    reversible_dmp_config['dof'] = 2
    dmp = ReversibleDMP(config=reversible_dmp_config)
    dmp.load_demo_trajectory(trajectory)
    dmp.train()

    return dmp

def test_reverse_dmp(dmp, speed=1., plot_trained=False, custom_start = None, custom_goal = None):
    test_config = reversible_dmp_config
    test_config['dt'] = 0.001

    # play with the parameters
    if custom_start is None:
        new_start = dmp._traj_data[-1, 1:] + np.zeros(reversible_dmp_config['dof'])
    else:
        new_start = custom_start

    if custom_goal is None:
        new_goal = dmp._traj_data[0, 1:] + np.zeros(reversible_dmp_config['dof'])
    else:
        new_goal = custom_goal

    external_force = np.zeros(reversible_dmp_config['dof'])
    alpha_phaseStop = 1.

    test_config['reversed_start'] = new_start
    test_config['reversed_goal'] = new_goal
    test_config['dy'] = np.zeros(reversible_dmp_config['dof'])
    test_config['tau'] = 1./speed
    test_config['ac'] = alpha_phaseStop
    test_config['type'] = 1

    if test_config['type'] == 1:
        test_config['extForce'] = external_force
    else:
        test_config['extForce'] = np.zeros(reversible_dmp_config['dof'])
    test_traj = dmp.generate_reverse_trajectory(config=test_config)

    if plot_trained:
        plot_traj([dmp._traj_data[:,1:], test_traj['pos'][:,1:]])

    test_traj = {
    'pos_traj': test_traj['pos'][:,1:],
    'vel_traj':test_traj['vel'][:,1:],
    'acc_traj':test_traj['acc'][:,1:]
    }
    
    return test_traj

if __name__ == '__main__':

    mt = MouseTracker(window_dim = [600, 400])

    # ----- record trajectory using mouse
    print "\nDraw trajectory ... "
    trajectory = mt.record_mousehold_path(record_interval = 0.01, close_on_mousebutton_up = True, verbose = False, inverted = True, keep_window_alive = True)

    # ----- get custom start and end points for the dmp using mouse clicks
    print "\nClick custom start and end points for the reversed trajectory"
    strt_end = mt.get_mouse_click_coords(num_clicks = 2, inverted = True, keep_window_alive = True, verbose = False)

    if trajectory.shape[0] > 0:
        dmp = train_dmp(trajectory)

        # ----- the trajectory after modifying the start and goal, speed etc. for the reverse path
        test_traj = test_reverse_dmp(dmp, speed=1.,plot_trained=False, custom_start = strt_end[0,:] if strt_end is not None else None, custom_goal = strt_end[1,:] if strt_end is not None else None)

        # ----- plotting the 2d paths (actual and modified)
        plot_path(test_traj, trajectory, custom_start = strt_end[0,:] if strt_end is not None else None, custom_goal = strt_end[1,:] if strt_end is not None else None)

    else:
        print "No data in trajectory!\n"
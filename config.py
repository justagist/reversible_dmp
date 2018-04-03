
D = 200.

reversible_dmp_config = {
        'end_time':1.0,
        'D':D,
        'K':D**2./4., 
        'rbf_num':1000, # number of basis function per DMP
        'tau':1.0,
        'ax':-3, # time constant of canonical system e+(ax)t
        'dt':0.001, # how fast the trajectory rolls out
        'original_scaling':1.,
        'type':1,
        'dof':2,
        'goal_thresh':None,
}
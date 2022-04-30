import torch
import numpy as np
import sigopt

from diffmd.training import Trainer

def run_and_track_in_sigopt():
    #   sigopt.log_dataset(DATASET_NAME)
    #   sigopt.log_metadata(key="Dataset Source", value=DATASET_SRC)
    #   sigopt.log_metadata(key="Feature Eng Pipeline Name", value=FEATURE_ENG_PIPELINE_NAME)
    #   sigopt.log_metadata(
    #     key="Dataset Rows", value=features.shape[0]
    #   )  # assumes features X are like a numpy array with shape
    #   sigopt.log_metadata(key="Dataset Columns", value=features.shape[1])
    #   sigopt.log_metadata(key="Execution Environment", value="Colab Notebook")
    
    sigopt.log_model('CG Hexagon Potential - Second Search')
    learning_rates = [10**i for i in range(-6, 2)]
    sigopt.params.setdefaults(
        # batch_length=np.random.randint(low=3, high=50),
        # nbatches=np.random.randint(low=10, high=1000),
        learning_rate=np.random.choice(learning_rates),
        nn_depth=np.random.randint(low=1, high=5),
        nn_width=np.random.randint(low=2, high=1000),
        # activation_function=,  
    )

    # TODO: add a script that creates experiment.yml based on config OR use this experiment function
    # experiment = sigopt.create_experiment(
    # name="Keras Model Optimization (Python)",
    # type="offline",
    # parameters=[
    #     dict(name="hidden_layer_size", type="int", bounds=dict(min=32, max=128)),
    #     dict(name="activation_function", type="categorical", categorical_values=["relu", "tanh"]),
    # ],
    # metrics=[dict(name="holdout_accuracy", objective="maximize")],
    # parallel_bandwidth=1,
    # budget=30,
    # )

    prefix = 'hexagons/trajectories/smooth/'
    dataset = 'NVE-temp-0.45_K-0.090702947845805_r-0_s-5'
    config = dict(
        filename = prefix+dataset, 
        device = torch.device("cpu"), 
        niters = 3000,
        optimizer = 'Adam',
        batch_length=20,
        nbatches=800,
        learning_rate=sigopt.params.learning_rate,
        nn_depth=sigopt.params.nn_depth,
        nn_width=sigopt.params.nn_width,
        activation_function=None,
        load_folder=None
        # load_folder='results/depth-1-width-300-lr-0.1',
    )

    sigopt.log_dataset(dataset) 
    
    trainer = Trainer(config)
    model, train_loss = trainer.train()
    trainer.save()

    # running_avg_train_loss = train_loss.avg
    current_train_loss = train_loss.val

    sigopt.log_metric(name="train_loss", value=current_train_loss)
    # sigopt.log_metric(name="test_loss", value=running_avg_test_loss)
    # sigopt.log_metric(name="training time (s)", value=traininx    g_time)
    # sigopt.log_metric(name="training and validation time (s)", value=training_and_validation_time)

run_and_track_in_sigopt()
# RUN sigopt optimize -e experiment.yml python sigopt-model.py > sigopt-model.out
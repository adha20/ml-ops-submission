import os
import tensorflow as tf
import tensorflow_transform as tft
import keras_tuner as kt
from tfx.components.trainer.fn_args_utils import FnArgs
from typing import NamedTuple, Dict, Text, Any

TunerFnResult = NamedTuple('TunerFnResult', [('tuner', kt.Tuner), ('fit_kwargs', Dict[Text, Any])])

LABEL_KEY = 'churn_xf'

NUMERIC_FEATURES = [
    'customer_age', 'monthly_charges', 'tenure', 
    'support_calls', 'total_usage', 'satisfaction_score',
    'gender', 'contract_type'
]

def transformed_name(key):
    return key + "_xf"

def gzip_reader_fn(filenames):
    """Loads compressed data"""
    return tf.data.TFRecordDataset(filenames, compression_type='GZIP')

def input_fn(file_pattern, tf_transform_output, num_epochs, batch_size=64):
    """Get post_transform feature & create batches of data"""
    transform_feature_spec = (
        tf_transform_output.transformed_feature_spec().copy())
    
    dataset = tf.data.experimental.make_batched_features_dataset(
        file_pattern=file_pattern,
        batch_size=batch_size,
        features=transform_feature_spec,
        reader=gzip_reader_fn,
        num_epochs=num_epochs,
        label_key=LABEL_KEY
    )
    
    return dataset

def model_builder(hp):
    """Builds the Keras model with hyperparameters."""
    input_features = []
    for key in NUMERIC_FEATURES:
        input_features.append(
            tf.keras.Input(shape=(1,), name=transformed_name(key))
        )
        
    x = tf.keras.layers.Concatenate()(input_features)
    
    hp_units_1 = hp.Int('units_1', min_value=16, max_value=64, step=16)
    hp_units_2 = hp.Int('units_2', min_value=8, max_value=32, step=8)
    hp_learning_rate = hp.Choice('learning_rate', values=[1e-2, 1e-3, 1e-4])

    x = tf.keras.layers.Dense(hp_units_1, activation='relu')(x)
    x = tf.keras.layers.Dense(hp_units_2, activation='relu')(x)
    outputs = tf.keras.layers.Dense(1, activation='sigmoid')(x)

    model = tf.keras.Model(inputs=input_features, outputs=outputs)
    
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=hp_learning_rate),
        loss='binary_crossentropy',
        metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall()]
    )
    
    return model

def tuner_fn(fn_args: FnArgs) -> TunerFnResult:
    """Build the tuner using the KerasTuner API."""
    tf_transform_output = tft.TFTransformOutput(fn_args.transform_graph_path)
    
    train_dataset = input_fn(fn_args.train_files, tf_transform_output, num_epochs=5)
    eval_dataset = input_fn(fn_args.eval_files, tf_transform_output, num_epochs=5)

    tuner = kt.RandomSearch(
        hypermodel=lambda hp: model_builder(hp),
        objective=kt.Objective('val_accuracy', direction='max'),
        max_trials=5,
        directory=fn_args.working_dir,
        project_name='kt_random_search'
    )

    return TunerFnResult(
        tuner=tuner,
        fit_kwargs={
            'x': train_dataset,
            'validation_data': eval_dataset,
            'steps_per_epoch': fn_args.train_steps,
            'validation_steps': fn_args.eval_steps
        }
    )

import os
import tensorflow as tf
import tensorflow_transform as tft
from tfx.components.trainer.fn_args_utils import FnArgs

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

def model_builder(hyperparameters):
    """Builds the Keras model with best hyperparameters."""
    input_features = []
    for key in NUMERIC_FEATURES:
        input_features.append(
            tf.keras.Input(shape=(1,), name=transformed_name(key))
        )
        
    x = tf.keras.layers.Concatenate()(input_features)
    
    hp_units_1 = hyperparameters.get('units_1', 32)
    hp_units_2 = hyperparameters.get('units_2', 16)
    hp_learning_rate = hyperparameters.get('learning_rate', 1e-3)

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

def _get_serve_tf_examples_fn(model, tf_transform_output):
    """Returns a function that parses a serialized tf.Example."""
    model.tft_layer = tf_transform_output.transform_features_layer()

    @tf.function
    def serve_tf_examples_fn(serialized_tf_examples):
        feature_spec = tf_transform_output.raw_feature_spec()
        feature_spec.pop('churn')
        parsed_features = tf.io.parse_example(serialized_tf_examples, feature_spec)
        transformed_features = model.tft_layer(parsed_features)
        return model(transformed_features)

    return serve_tf_examples_fn

def run_fn(fn_args: FnArgs):
    """Train a churn prediction model using the transformed dataset."""
    tf_transform_output = tft.TFTransformOutput(fn_args.transform_graph_path)

    train_dataset = input_fn(fn_args.train_files, tf_transform_output, num_epochs=10)
    eval_dataset = input_fn(fn_args.eval_files, tf_transform_output, num_epochs=10)

    hyperparameters = fn_args.hyperparameters
    if hyperparameters is None:
        hyperparameters = {}
    
    model = model_builder(hyperparameters)
    
    model.fit(
        train_dataset,
        steps_per_epoch=fn_args.train_steps,
        validation_data=eval_dataset,
        validation_steps=fn_args.eval_steps,
        epochs=10
    )

    signatures = {
        'serving_default':
            _get_serve_tf_examples_fn(model, tf_transform_output).get_concrete_function(
                tf.TensorSpec(shape=[None], dtype=tf.string, name='examples'))
    }
    
    model.save(fn_args.serving_model_dir, save_format='tf', signatures=signatures)

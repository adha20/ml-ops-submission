import tensorflow as tf
import tensorflow_transform as tft

NUMERIC_FEATURES = [
    'customer_age',
    'monthly_charges',
    'tenure',
    'support_calls',
    'total_usage',
    'satisfaction_score'
]

def transformed_name(key):
    """Renaming transformed features."""
    return key + "_xf"

def preprocessing_fn(inputs):
    """Create transformed features for the churn classifier."""
    outputs = {}

    for feature_name in NUMERIC_FEATURES:
        outputs[transformed_name(feature_name)] = tft.scale_to_z_score(inputs[feature_name])

    outputs[transformed_name('gender')] = tf.where(
        tf.equal(inputs['gender'], 'Male'),
        tf.constant(1.0),
        tf.constant(0.0),
    )
    
    outputs[transformed_name('contract_type')] = tf.where(
        tf.equal(inputs['contract_type'], 'Month-to-Month'),
        tf.constant(1.0),
        tf.where(tf.equal(inputs['contract_type'], 'One Year'), tf.constant(2.0), tf.constant(3.0)),
    )
    
    # Do not transform the label here, trainer will handle it, or we can just pass it through.
    # TFX Pipeline usually passes the label directly to Trainer if not transformed.
    # Wait, the Evaluator and Trainer expect the label. It's safer to pass the label through if we use the transformed graph.
    outputs[transformed_name('churn')] = tf.cast(inputs['churn'], tf.int64)

    return outputs

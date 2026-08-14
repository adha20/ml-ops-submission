import os
from typing import Optional

from tfx import v1 as tfx
from tfx.orchestration import metadata
from tfx.orchestration.beam.beam_dag_runner import BeamDagRunner
from tfx.proto import example_gen_pb2, trainer_pb2, pusher_pb2
import tensorflow_model_analysis as tfma


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
PIPELINE_ROOT = os.path.join(PROJECT_ROOT, "muhammad_adha-pipeline")
PIPELINE_NAME = "customer_churn_tfx_pipeline"


# TFX pipeline components

def create_pipeline(pipeline_name: str = PIPELINE_NAME, pipeline_root: str = PIPELINE_ROOT) -> tfx.dsl.Pipeline:
    """Build a simple end-to-end TFX pipeline for churn prediction."""
    example_gen = tfx.components.CsvExampleGen(
        input_base=DATA_DIR,
        output_config=example_gen_pb2.Output(
            split_config=example_gen_pb2.SplitConfig(
                splits=[
                    example_gen_pb2.SplitConfig.Split(name='train', hash_buckets=8),
                    example_gen_pb2.SplitConfig.Split(name='eval', hash_buckets=2),
                ]
            )
        ),
    )

    statistics_gen = tfx.components.StatisticsGen(
        examples=example_gen.outputs['examples'],
    )

    schema_gen = tfx.components.SchemaGen(
        statistics=statistics_gen.outputs['statistics'],
        infer_feature_shape=True,
    )

    example_validator = tfx.components.ExampleValidator(
        statistics=statistics_gen.outputs['statistics'],
        schema=schema_gen.outputs['schema'],
    )

    transform = tfx.components.Transform(
        examples=example_gen.outputs['examples'],
        schema=schema_gen.outputs['schema'],
        module_file=os.path.join(PROJECT_ROOT, 'modules', 'transform_module.py'),
    )

    tuner = tfx.components.Tuner(
        module_file=os.path.join(PROJECT_ROOT, 'modules', 'tuner_module.py'),
        examples=transform.outputs['transformed_examples'],
        transform_graph=transform.outputs['transform_graph'],
        schema=schema_gen.outputs['schema'],
        train_args=trainer_pb2.TrainArgs(splits=['train'], num_steps=20),
        eval_args=trainer_pb2.EvalArgs(splits=['eval'], num_steps=5),
    )

    trainer = tfx.components.Trainer(
        module_file=os.path.join(PROJECT_ROOT, 'modules', 'trainer_module.py'),
        examples=transform.outputs['transformed_examples'],
        transform_graph=transform.outputs['transform_graph'],
        schema=schema_gen.outputs['schema'],
        hyperparameters=tuner.outputs['best_hyperparameters'],
        train_args=trainer_pb2.TrainArgs(splits=['train'], num_steps=100),
        eval_args=trainer_pb2.EvalArgs(splits=['eval'], num_steps=20),
    )

    # Resolver step: select the latest valid model artifact to support evaluation or pushing.
    latest_model_resolver = tfx.dsl.Resolver(
        strategy_class=tfx.dsl.experimental.LatestBlessedModelStrategy,
        model=trainer.outputs['model'],
        model_blessing=tfx.dsl.Channel(type=tfx.types.standard_artifacts.ModelBlessing),
    ).with_id('latest_model_resolver')

    eval_config = tfma.EvalConfig(
        model_specs=[tfma.ModelSpec(label_key='churn')],
        slicing_specs=[tfma.SlicingSpec()],
        metrics_specs=[
            tfma.MetricsSpec(metrics=[
                tfma.MetricConfig(class_name='ExampleCount'),
                tfma.MetricConfig(class_name='BinaryAccuracy',
                    threshold=tfma.MetricThreshold(
                        value_threshold=tfma.GenericValueThreshold(
                            lower_bound={'value': 0.5}),
                        change_threshold=tfma.GenericChangeThreshold(
                            direction=tfma.MetricDirection.HIGHER_IS_BETTER,
                            absolute={'value': -1e-10})))
            ])
        ]
    )

    evaluator = tfx.components.Evaluator(
        examples=example_gen.outputs['examples'],
        model=trainer.outputs['model'],
        baseline_model=latest_model_resolver.outputs['model'],
        eval_config=eval_config,
    )

    serving_path = os.path.join(PROJECT_ROOT, 'app', 'model_store')
    os.makedirs(serving_path, exist_ok=True)

    pusher = tfx.components.Pusher(
        model=trainer.outputs['model'],
        push_destination=pusher_pb2.PushDestination(
            filesystem=pusher_pb2.PushDestination.Filesystem(
                base_directory=serving_path,
            )
        ),
    )

    return tfx.dsl.Pipeline(
        pipeline_name=pipeline_name,
        pipeline_root=pipeline_root,
        metadata_connection_config=metadata.sqlite_metadata_connection_config(
            os.path.join(pipeline_root, 'metadata.db')
        ),
        components=[
            example_gen,
            statistics_gen,
            schema_gen,
            example_validator,
            transform,
            tuner,
            trainer,
            latest_model_resolver,
            evaluator,
            pusher,
        ],
    )


if __name__ == '__main__':
    pipeline = create_pipeline()
    BeamDagRunner().run(pipeline)
    print(f'Pipeline "{PIPELINE_NAME}" has been submitted to Beam.')

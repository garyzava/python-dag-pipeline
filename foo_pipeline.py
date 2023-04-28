#from multiprocessing import Process
import dag_pipeline
import foo_jobs
import yaml

def main():

    # Read stages from yaml file
    with open("stages.yaml") as file:
        stages = yaml.safe_load(file)

    print("Stages from YAML:- ", stages)

    # Create a DagPipeline object
    pipeline = dag_pipeline.DagPipeline(stages)
    print("Sorted Pipeline:- ", pipeline.get_result())

    # Execute the stages (jobs)
    print("###Start Foo Jobs###")
    pipeline.run(foo_jobs)
    print("###End Foo Jobs###")

if __name__ == "__main__":
    main()
# Lightweight Python Pipeline

This Python pipeline is designed to facilitate the creation of Directed Acyclic Graphs (DAGs) based on dependencies. With this tool, you no longer need to worry about the prerequisites of each node within your workflow pipeline. The pipeline is lightweight and easy to use, making it a great choice for Python developers who want to streamline their Python workflows.

## Prerequisites

Install the following python packages

```
pip install networkx
pip install multiprocess
pip install pyyaml
```

or simply install the requirements.txt file

```
pip install -r requirements.txt
```

## Background

### Data pipeline process
To understand how a data pipeline works, think of any pipe that receives something from a source and carries it to a destination. What happens to the data along the way depends upon the business use case and the destination itself. A data pipeline may be a simple process of data extraction and loading, or, it may be designed to handle data in a more advanced manner, such as training datasets for machine learning.

### Defining the dependencies in a human readable format

Another common use case is to define the dependencies between the stages of a pipeline in a human readable format. This allows the pipeline to be easily modified and extended. For example, the following YAML file defines the dependencies between the stages of a pipeline:

```yaml
# Define the stages and their dependencies of a data pipeline in a human-friendly way
Lint: []
Test: []
Coverage:
  - Test
Docs:
  - Coverage
  - Lint
Benchmark:
  - Coverage 
```

### Making the pipeline reexecutable

A key use case, that will make the life of your DataOps team easy, is for the pipeline to be able to be re-executed without having to re-run the stages that have already been executed. This allows the pipeline to be run multiple times without having to re-run the stages that have already been executed. For example, if the pipeline is run twice, the second run should only execute the stages that have not yet been executed.

This is achieved by storing the state of the pipeline in a YAML file named state.yml. The state of the pipeline is stored in the following format:

```yaml
Benchmark: null
Coverage: FAILED
Docs: null
Lint: SUCCESS
Test: SUCCESS
```

You can see above that the Benchmark stage has not yet been executed, the Coverage stage has failed, the Docs stage has not yet been executed, the Lint stage has succeeded, and the Test stage has succeeded.

## Usage

Execute the following command to run the pipeline:

```bash
python foo_pipeline.py
```

### Workflow

The first step of the workflow is defined in a YAML file. The pipeline requires three scripts to run and a YAML file to define the stages of the pipeline:

* **dag_pipeline.py** - This script defines the DagPipeline class, which is a lightweight pipeline framework that allows users to create directed acyclic graphs (DAGs) of jobs based on their dependencies.
* **foo_jobs.py** - This script defines the jobs that are executed by the pipeline.
* **foo_pipeline.py** - This script runs the pipeline of jobs defined in a YAML file.
* **stages.yaml** - This YAML file defines the stages of the pipeline.

### dag_pipeline.py

This code defines a class named DagPipeline that takes a dictionary of dependencies between stages and sorts them to enable parallel runs. The class uses the networkx library to build a directed graph of the dependencies and performs a topological sort to determine the order of the stages.

The __init__ method of the class takes the dependencies dictionary as input and initializes various instance variables, including self.dependencies, self.g, self.out_degree_map, self.zero_out_degree, self.result, and self.cycles. It also calls the sort_jobs method, which sorts the stages in the pipeline and raises an exception if there are any cycles in the graph.

The sort_jobs method performs a topological sort of the pipeline stages and stores the order in the self.result instance variable. It uses the self.zero_out_degree and self.out_degree_map variables to keep track of the stages that have zero out-degree and the out-degree of each stage, respectively.

The load_state and save_state methods read and write the state of the pipeline from/to a YAML file named state.yml.

The run method executes the stages of the pipeline in the order determined by the sort_jobs method. If a stage has not yet been executed or has failed, it is submitted to a thread pool for execution. The run_task method is responsible for running a single stage and updating the state of the pipeline accordingly. The check_dependencies method checks if the dependencies of a stage have been satisfied before it is executed.

The class uses the logging module to log various messages to the console and a log file. It also uses the concurrent.futures module to run the stages in parallel.

### foo_pipeline.py

This is a Python script that runs a pipeline of jobs (called "stages" in the code) defined in a YAML file (stages.yaml).

The script first reads the YAML file and loads the stages into a list of dictionaries called stages. It then creates a DagPipeline object from the dag_pipeline module, passing in the stages list as an argument. The get_result method of the DagPipeline object returns a sorted list of jobs based on their dependencies.

After printing out the sorted pipeline, the script executes the stages by calling the run method of the DagPipeline object, passing in a module called foo_jobs as an argument. The run method executes the stages sequentially or concurrently depending on their dependencies.

## Resources
* **thomaspoignant** - *Inspiration* - [sort_pipeline_example.py](https://gist.github.com/garyzava/83f10a6bc0d6a4a61940fbeb95d62072)
* **pditommaso** - *Comprehensive of Pipelines* -[Awesome-pipeline](https://github.com/pditommaso/awesome-pipeline)

from typing import Dict, List, Optional
import networkx as nx

from multiprocessing import Process
import concurrent.futures

import yaml
import logging

from datetime import datetime

class DagPipeline:
    """"
    DagPipeline takes a dependency dict and sort the jobs to be able to have parallel run.
    """
    def __init__(self, dependencies: Dict[str, List[str]]):
        print("depen:- ", dependencies)

        self.state_file = "state.yml"
        self.logger = logging.getLogger(__name__)
        #self.logger.setLevel(logging.DEBUG)
        #self.logger.addHandler(logging.StreamHandler())

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

        self.stdout_handler = logging.StreamHandler()
        self.stdout_handler.setLevel(logging.DEBUG)
        self.stdout_handler.setFormatter(self.formatter)

        self.file_handler = logging.FileHandler(__file__ + '-' + datetime.now().strftime("%Y%m%d%H%M%S") + '.log')
        self.file_handler.setLevel(logging.INFO)
        self.file_handler.setFormatter(self.formatter)

        self.logger.addHandler(self.file_handler)
        self.logger.addHandler(self.stdout_handler)        

        self.dependencies = dependencies
        self.g = nx.DiGraph(dependencies)
        self.out_degree_map = {v: d for v, d in self.g.out_degree() if d > 0}
        self.zero_out_degree = [v for v, d in self.g.out_degree() if d == 0]
        self.result = []
        self.cycles = list(nx.simple_cycles(self.g))
        self.sort_jobs()

    def sort_jobs(self):
        """
        sort_jobs is taking a dependency dict and sort the jobs to be able to have parallel run.
        :param dependencies: A dependency dict that contains every stages and their dependencies
                             something like { "1": [], "2": [], "3": ["2", "1", "4"], "4": ["2", "1"] }
        :return:  The order of the stages
                  example: [["1", "2"], ["4"], ["3"]]
        """
        # detect cycling workflows
        if len(self.cycles) > 0:
            raise CyclingPipeline(cycles=self.cycles)

        # sort the stages
        while self.zero_out_degree:
            self.result.append(self.zero_out_degree)
            new_zero_out_degree = []
            for v in self.zero_out_degree:
                for child, _ in self.g.in_edges(v):
                    self.out_degree_map[child] -= 1
                    if not self.out_degree_map[child]:
                        new_zero_out_degree.append(child)
            self.zero_out_degree = new_zero_out_degree

    def get_result(self):
        return self.result

    def load_state(self):
        try:
            with open(self.state_file, "r") as f:
                state = yaml.safe_load(f)
        except FileNotFoundError:
            
            #state = {name: None for name in self.nodes}
            #check if this is correct
            #state = {}
            #print("self.result:- ", self.g.nodes )
            state = {x: None for x in self.g.nodes}
            #print("state:-", state)
            pass
        return state
    
    def save_state(self, state):
        with open(self.state_file, "w") as f:
            yaml.safe_dump(state, f)    

    def check_dependencies(self, state, task_name):
        ''' returns true if all dependencies are satisfied '''        
        for dep in self.dependencies[task_name]:
            if state[dep] != "SUCCESS" or state[dep] is None:
                return False
        return True


    #def run(self, task_name=None, *args):
    def run(self, *args):
        task_name=None # TO-DO
        state = self.load_state()
        if task_name:
            print("task_name:- ", task_name)
            self.run_task(task_name, state)
        else:
            for jobs_to_run in self.result:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    for job in jobs_to_run:
                        if state[job] != "SUCCESS":
                            executor.submit(self.run_task, job, state, *args)
                        elif state[job] == "SUCCESS":
                            self.logger.debug(f"Job {job} already completed, skipping")
                            #print(f"Job {job} already completed, skipping")
                            pass
                        else:
                            #check if this else block is needed
                            self.logger.debug(f"Dependencies for {job} not satisfied, skipping")
                            print(f"Dependencies for {job} not satisfied, skipping")
                            return

        self.save_state(state)

    def run_task(self, task_name, state, *args):
        if not self.check_dependencies(state, task_name):
            self.logger.debug(f"Dependencies for {task_name} not satisfied, skipping")
            return
        try:
            state[task_name] = "RUNNING"
            self.logger.info(f"Running {task_name}")

            getattr(*args, task_name)()

            state[task_name] = "SUCCESS"
            self.logger.info(f"{task_name} completed successfully")
        except Exception as e:
            self.logger.exception(f"{task_name} failed")
            state[task_name] = "FAILED"                

    def test_function(self, *args):
        print("args:- ", *args)
        for jobs_to_run in self.result:

            with concurrent.futures.ThreadPoolExecutor() as executor:
                print("jobs_to_run:- ", jobs_to_run)
                executor.map(lambda job: getattr(*args, job)(), jobs_to_run)

    def run_concurrently(self):
        """
        run_concurrently runs the stages concurrently
        :return:
        """
        with concurrent.futures.ProcessPoolExecutor() as executor:
            executor.map(self.run_pipeline, self.result)

    def run_pipeline(self):
        """
        run the sorted stages
        :return:
        """
        for i in self.result:
            if len(i) == 1:
                getattr(self, i[0])()
            else:
                RunConcurrently(*[getattr(self, item) for item in i])

class RunConcurrently:
    """
    RunConcurrently takes a list of jobs and run them concurrently.
    """    
    def __init__(self, *args):
        self.args = args
        self.processes = []
        self.run()

    def run(self):
        for arg in self.args:
            p = Process(target=arg)
            p.start()
            self.processes.append(p)
        for p in self.processes:
            p.join()



class CyclingPipeline(Exception):
    """
    CyclingPipeline is an exception raised if we detect a cycle in the pipeline.
    """
    def __init__(self, cycles=Optional[List]):
        self.cycles = cycles
        super().__init__(f"CyclingPipeline: {cycles}")


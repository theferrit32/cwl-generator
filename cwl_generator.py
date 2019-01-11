#!/bin/env python3
import sys
import random as rnd
import time
import datetime
import logging
import argparse
import networkx as nx
import yaml
import json
import copy
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def now_str():
    return datetime.datetime.now().isoformat()

def yaml_dump(dictionary):
    return yaml.dump(dictionary, default_flow_style=False)

"""
See: https://github.com/heliumdatacommons/pivot-scheduling/blob/86be8d51f3546c85aac0095609a46665baae7dea/appliance/gen.py
"""
class RandomDAGGenerator(object):

  def __init__(self, n_nodes_lo, n_nodes_hi, edge_den_lo, edge_den_hi, seed=None):
    """
    :param n_nodes_lo: lower bound of number of nodes
    :param n_nodes_hi: upper bound of number of nodes
    :param edge_den_lo: lower bound of edge density
    :param edge_den_hi: upper bound of edge density
    :param seed: random seed
    """
    assert 1 < n_nodes_lo <= n_nodes_hi
    assert 0 < edge_den_lo <= edge_den_hi <= 1
    self.__n_nodes_lo = n_nodes_lo
    self.__n_nodes_hi = n_nodes_hi
    self.__edge_den_lo = edge_den_lo
    self.__edge_den_hi = edge_den_hi
    self.__seed = seed
    rnd.seed(seed)

  def generate(self):
    n_nodes = int(rnd.uniform(self.__n_nodes_lo, self.__n_nodes_hi))
    edge_den = rnd.uniform(self.__edge_den_lo, self.__edge_den_hi)
    g = nx.fast_gnp_random_graph(n_nodes, edge_den, seed=self.__seed, directed=True)
    return nx.DiGraph([(u, v) for u, v in g.edges() if u < v])


class RandomWorkflowGenerator(object):
    def __init__(self,
            data_min, data_max, 
            cpu_min, cpu_max, 
            mem_min, mem_max,
            disk_min, disk_max,
            gpu_min, gpu_max,
            parallel_jobs=10,
            seed=None,
            command="sha256sum {file}"):
        """
        :param dagGenerator: object which generates a directed acyclic graph with .generate()
        :param data_min: lower bound of size of data file to use (MiB)
        :param data_max: upper bound of size of data file to use (MiB)
        :param TODO fill in
        """
        #assert isinstance(dagGenerator, RandomDAGGenerator)
        #self.dagGenerator = dagGenerator
        self.data_min = data_min
        self.data_max = data_max
        self.cpu_min = cpu_min
        self.cpu_max = cpu_max
        self.mem_min = mem_min
        self.mem_max = mem_max
        self.disk_min = disk_min
        self.disk_max = disk_max
        self.gpu_min = gpu_min
        self.gpu_max = gpu_max
        self.parallel_jobs = parallel_jobs
        self.seed = seed
        self.command = command
        #TODO validate ranges
        #args = locals()
        #for k,v in [x for x in locals().items() if x[0] != 'self']:
        #    setattr(self, str(k), v)
    
    def generate(self):
        #graph = self.dagGenerator.generate()
        if self.seed is not None:
            rnd.seed(self.seed)
        else:
            rnd.seed(time.time())
        data = rnd.uniform(self.data_min, self.data_max)
        cpu = rnd.uniform(self.cpu_min, self.cpu_max)
        mem = rnd.uniform(self.mem_min, self.mem_max)
        disk = rnd.uniform(self.disk_min, self.disk_max)
        gpu = rnd.uniform(self.gpu_min, self.gpu_max)
        workflow_id = "cwl_generator"#_{0}".format(now_str().replace(":", "-"))
        workflow = {
            "cwlVersion": "v1.0",
            "class": "Workflow",
            "id": workflow_id,
            "inputs": [],
            "outputs": {
                "files_out": {
                    "type": "File[]",
                    "outputSource": []
                }
            },
            "steps": [], # this is a surprise field that can help us later
            "requirements": [
                {"class": "StepInputExpressionRequirement"},
                {"class": "ScatterFeatureRequirement"},
                {"class": "MultipleInputFeatureRequirement"}
            ]
        }
        generate_job_prefix = "generate_file_"
        generated_file_prefix = "data_file_"
        generate_job = {
            "id": generate_job_prefix,
            "run": "dd.cwl",
            "in": {
                "block_size": {
                    "default": "10M"
                },
                "count": {
                    "default": 2
                },
                "output_filename": {
                    "default": generated_file_prefix
                }
            },
            "out": ["file_out"]
        }
        hash_job_prefix = "hash_file_"
        hash_job = {
            "id": hash_job_prefix,
            "run": "sha256.cwl",
            "in": {
                "filename": ""
            },
            "out": ["hash"]
        }

        # add file generation jobs
        for i in range(self.parallel_jobs):
            j = copy.deepcopy(generate_job)
            j["id"] += str(i)
            j["in"]["output_filename"]["default"] += str(i)
            workflow["steps"].append(j)
            # add workflow output
            workflow["outputs"]["files_out"]["outputSource"].append(
                "#{}{}/file_out".format(generate_job_prefix, str(i)))

        # add hash jobs
        for i in range(self.parallel_jobs):
            j = copy.deepcopy(hash_job)
            j["id"] += str(i)
            j["in"]["filename"] = "#{}{}/file_out".format(generate_job_prefix, str(i))
            workflow["steps"].append(j)

        return workflow


def main(argv):
    parser = argparse.ArgumentParser(description="Generate a random workflow for testing purposes")
    format_group = parser.add_mutually_exclusive_group(required=False)
    format_group.add_argument("--yaml", default=False, action="store_true", help="Output workflow in YAML (default)")
    format_group.add_argument("--json", default=False, action="store_true", help="Output workflow in JSON")

    opts = parser.parse_args(argv)
    if not opts.yaml and not opts.json:
        opts.yaml = True

    #dagGenerator = RandomDAGGenerator(10, 20, 0.5, 0.5, seed=1)
    wfGenerator = RandomWorkflowGenerator(
            10, 20,
            1, 2,
            256, 512,
            256, 512,
            0, 0,
            seed=2)

    wf = wfGenerator.generate()
    
    if opts.yaml:
        wf_string = yaml.dump(wf, default_flow_style=False)
    elif opts.json:
        wf_string = json.dumps(wf, indent=2) # match default yaml indent of 2 spaces
    #print(wf_json)
    filename = wf["id"] + ".cwl"
    with open(filename, "w") as f:
        logger.debug("writing output file: {0}".format(filename))
        f.write(wf_string)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
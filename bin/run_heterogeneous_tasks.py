#!/usr/bin/env python

import os
import sys

import radical.pilot as rp
import radical.utils as ru

from random import randint


# -----------------------------------------------------------------------------
def unique_sums_cpu(numbers, target, partial=[], sums=[]):

    s = sum(partial)

    # check if the partial sum is equals to target
    if s == target:
        return sums.append(partial)

    # we overshoot
    if s >= target:
        return sums

    for i in range(len(numbers)):
        n = numbers[i]
        remaining = numbers[i + 1:]
        unique_sums_cpu(remaining, target, partial + [n], sums)

    # nothing else to do
    return sums


# -----------------------------------------------------------------------------
def unique_sums_gpu(numbers, target, partial=[], sums=[]):

    s = sum(partial)

    # check if the partial sum is equals to target
    if s == target:
        return sums.append(partial)

    # we overshoot
    if s >= target:
        return sums

    for i in range(len(numbers)):
        n = numbers[i]
        remaining = numbers[i + 1:]
        unique_sums_gpu(remaining, target, partial + [n], sums)

    # nothing else to do
    return sums


# -----------------------------------------------------------------------------
def fill_node_cpu(nnodes, ncores):

    cores=[]

    # unique_sums returns multiple elements so we can overshoot
    while len(cores) <= nnodes:
        sums = unique_sums_cpu(range(1, ncores), ncores)
        cores.extend(sums)


    # trim cores in case we overshoot
    cores = cores[:nnodes]
    return cores


# -----------------------------------------------------------------------------
def fill_node_gpu(nnodes, ncores):

    cores=[]

    # unique_sums returns multiple elements so we can overshoot
    while len(cores) <= nnodes:
        sums = unique_sums_gpu(range(1, ncores), ncores)
        cores.extend(sums)


    # trim cores in case we overshoot
    cores = cores[:nnodes]
    return cores


# -----------------------------------------------------------------------------
def merge_gpus_cpus(gpus, cpus):

    lg = len(gpus)
    lc = len(cpus)
    tasks_node = []

    if lg == lc:
        for i in range(0, lg):
            tasks_node.append([gpus[i], cpus[i]])
    else:
        raise Exception("GPUs/CPUs per node mismatch:\n%i != %i" % (lg, lc))

    # Account for the cores needed for each GPU task.
    tasks_node_norm = []
    for tasks in tasks_node:
        ncores_gpus = len(tasks[0])
        if any(i > ncores_gpus for i in tasks[1]):
            tasks[1].sort()
            new_cpus_tasks = [tasks[1][-1]-ncores_gpus if item == tasks[1][-1] else item for item in tasks[1]]
        else:
            raise Exception("ERROR: implement sum within tasks[1]")
        tasks_node_norm.append([tasks[0], new_cpus_tasks])

    return tasks_node_norm


# -----------------------------------------------------------------------------
def sanity_check(tn, n, gn, cn):

    if len(tn) != n:
        return "Task/node mismatch: tasks: %i; nodes: %i" % (len(tn), n)

    for t in tn:
        if sum(t[0]) != gn:
            return "GPU per node mismatch"
        if sum(t[1]) != (cn - len(t[0])):
            return "CPU cores per node mismatch"

    return "pass"


# =============================================================================
if __name__ == '__main__':

    # reporter
    reporter = ru.Reporter(name='radical.pilot')
    reporter.title('Getting Started (RP version %s)' % rp.version)

    # resource specified as argument
    if len(sys.argv) == 6: 
        resource = sys.argv[1]
        nodes = int(sys.argv[2])
        queue = sys.argv[3]
        gens = int(sys.argv[4])
        subagents = int(sys.argv[5])
    else: 
        reporter.exit('Usage:\t%s [resource] [number_of_nodes] [queue] [generations] [number of sub-agents]\n\n' % sys.argv[0])

    # Create a session.
    session = rp.Session()

    try:

        # setup managers and resources
        pmgr   = rp.PilotManager(session=session)
        umgr   = rp.UnitManager(session=session)
        
        pd_init = {'resource'      : resource,
                   'runtime'       : 120,
                   'exit_on_error' : True,
                   'project'       : 'csc343',
                   'queue'         : queue,
                   'cores'         : nodes * 168,
                   'gpus'          : nodes * 6
                  }
        pdesc = rp.ComputePilotDescription(pd_init)
        
        pilot = pmgr.submit_pilots(pdesc)
        umgr.add_pilots(pilot)

        # how many GPUs and CPU cores per node. We researve always at least 
        # one for the GPU
        gpus_node = 6
        cores_node = 42

        # each subagent requires a node. No workload runs on subagent nodes
        wrkl_nodes = nodes - subagents

        # n distinct combinations of task sizes to occpy a node
        # FIXME: concot a function that does not retain memory after its
        # execution.
        tasks_gpu = fill_node_gpu(wrkl_nodes, gpus_node)
        tasks_cpu = fill_node_cpu(wrkl_nodes, cores_node)
        tasks_node = merge_gpus_cpus(tasks_gpu, tasks_cpu)

        # we use an heuristic: sanity check
        report = sanity_check(tasks_node, wrkl_nodes, gpus_node, cores_node)
        if report != "pass":
            raise Exception(report)

        # Add task generation
        tasks_node = tasks_node * gens

        # count the number of tasks
        ntasks = sum([len(j) for i in tasks_node for j in i])
        reporter.header("submit %d units" % ntasks)
        print("DEBUG: gpu/cpu processes peer node: %s" % tasks_node)

        # report we are starting to create the RP tasks
        reporter.progress_tgt(ntasks, label='create')

        cuds = list()
        for tasks in tasks_node:
            # gpu processes
            for pgpu in tasks[0]:

                cud = rp.ComputeUnitDescription()
                cud.executable = '/ccs/home/mturilli1/bin/hello_rp.sh'
                cud.arguments  = [randint(60, 300) * 1]
                cud.gpu_processes = pgpu
                cud.gpu_process_type = rp.POSIX
                cud.cpu_processes = 1
                cud.cpu_threads = 4
                cuds.append(cud)

            for pcpu in tasks[1]:

                cud = rp.ComputeUnitDescription()
                cud.executable = '/ccs/home/mturilli1/bin/hello_rp.sh'
                cud.arguments  = [randint(300, 900) * 1]
                cud.cpu_processes = pcpu
                cud.cpu_threads = 4
                cud.cpu_process_type = rp.POSIX
                cuds.append(cud)

        reporter.progress_done()

        # submit tasks
        umgr.submit_units(cuds)
        umgr.wait_units()

    except Exception as e:
        # Something unexpected happened in the pilot code above
        reporter.error('caught Exception: %s\n' % e)
        ru.print_exception_trace()
        raise

    except (KeyboardInterrupt, SystemExit):
        # the callback called sys.exit(), and we can here catch the
        # corresponding KeyboardInterrupt exception for shutdown.  We also catch
        # SystemExit (which gets raised if the main threads exits for some other
        # reason).
        ru.print_exception_trace()
        reporter.warn('exit requested\n')

    finally:
        # always clean up the session, no matter if we caught an exception or
        # not.  This will kill all remaining pilots.
        reporter.header('finalize')
        session.close(download=True)

    reporter.header()


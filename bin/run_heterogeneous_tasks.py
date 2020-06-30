#!/usr/bin/env python

import os
import sys

import radical.pilot as rp
import radical.utils as ru

from random import randint

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



def fill_node_cpu(nnodes, ncores):

    cores=[]

    # unique_sums returns multiple elements so we can overshoot
    while len(cores) <= nnodes:
        sums = unique_sums_cpu(range(1, ncores), ncores)
        cores.extend(sums)


    # trim cores in case we overshoot
    cores = cores[:nnodes]
    return cores


def fill_node_gpu(nnodes, ncores):

    cores=[]

    # unique_sums returns multiple elements so we can overshoot
    while len(cores) <= nnodes:
        sums = unique_sums_gpu(range(1, ncores), ncores)
        cores.extend(sums)


    # trim cores in case we overshoot
    cores = cores[:nnodes]
    return cores


def merge_gpus_cpus(gpus, cpus):

    lg = len(gpus)
    lc = len(cpus)
    tasks_node = []

    if lg == lc:
        for i in range(0, lg):
            tasks_node.append([gpus[i], cpus[i]])
    else:
        raise Exception("GPUs/CPUs per node mismatch:\n%i != %i" % (lg, lc))

    return tasks_node


def sanity_check(tn, n, gn, cn):

    if len(tn) != n:
        return "Task/node mismatch: tasks: %i; nodes: %i" % (len(tn), n)

    for t in tn:
        if sum(t[0]) != gn:
            return "GPU per node mismatch"
        if sum(t[1]) != cn:
            return "CPU cores per node mismatch"

    return "pass"

# ------------------------------------------------------------------------------
if __name__ == '__main__':

    # reporter
    reporter = ru.Reporter(name='radical.pilot')
    reporter.title('Getting Started (RP version %s)' % rp.version)

    # resource specified as argument
    if len(sys.argv) == 2: 
        resource = sys.argv[1]
    else: 
        reporter.exit('Usage:\t%s [resource]\n\n' % sys.argv[0])

    # Create a session.
    session = rp.Session()

    try:

        # setup managers and resources
        pmgr   = rp.PilotManager(session=session)
        umgr   = rp.UnitManager(session=session)
        
        pd_init = {'resource'      : resource,
                   'runtime'       : 60,
                   'exit_on_error' : True,
                   'project'       : 'csc343',
                   'queue'         : 'debug',
                   'cores'         : 168,
                   'gpus'          : 6
                  }
        pdesc = rp.ComputePilotDescription(pd_init)
        
        pilot = pmgr.submit_pilots(pdesc)
        umgr.add_pilots(pilot)

        # how many nodes we want
        nodes = 1 #23

        # how many GPUs and CPU cores per node. We researve always at least one
        gpus_node = pd_init['gpus']
        cores_node = int(pd_init['cores']/4)

        # n distinct combinations of task sizes to occpy a node
        # FIXME: concot a function that does not retain memory after its
        # execution.
        tasks_gpu = fill_node_gpu(nodes, gpus_node)
        tasks_cpu = fill_node_cpu(nodes, cores_node)
        tasks_node = merge_gpus_cpus(tasks_gpu, tasks_cpu)

        # we use an heuristic: sanity check
        report = sanity_check(tasks_node, nodes, gpus_node, cores_node)
        if report != "pass":
            raise Exception(report)

        # count the number of tasks
        ntasks = sum([len(i) for i in tasks_node])
        reporter.header("submit %d units" % ntasks)

        # report we are starting to create the RP tasks
        reporter.progress_tgt(ntasks, label='create')

        cuds = list()
        for tasks in tasks_node:
            # gpu processes
            for pgpu in tasks[0]:

                cud = rp.ComputeUnitDescription()
                cud.executable = '/ccs/home/mturilli1/bin/hello_rp.sh'
                cud.arguments  = [randint(5, 10) * 1]
                cud.gpu_processes = pgpu
                cud.gpu_process_type = rp.POSIX
                cuds.append(cud)

            for pcpu in tasks[1]:

                cud = rp.ComputeUnitDescription()
                cud.executable = '/ccs/home/mturilli1/bin/hello_rp.sh'
                cud.arguments  = [randint(5, 10) * 1]
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

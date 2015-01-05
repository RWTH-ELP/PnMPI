#!/usr/bin/python
# -*- coding: utf-8 -*-

# -*- python -*-
#
# Copyright (c) 2008, Lawrence Livermore National Security, LLC.
# Written by Martin Schulz, schulzm@llnl.gov, LLNL-CODE-402774,
# All rights reserved - please read information in "LICENCSE"
#
#   mpiP MPI Profiler ( http://mpip.sourceforge.net/ )
#
#   Please see COPYRIGHT AND LICENSE information at the end of this file.
#
#
#   make-wrappers.py -- parse the mpi prototype file and generate a
#     series of output files, which include the wrappers for profiling
#     layer and other data structures.
#
#   $Id: makefortran.py,v 1.2 2008/03/09 03:50:47 schulz Exp $
#

import sys
import string
import os
import copy
import re
import time
import getopt
import socket
import pdb

cnt = 0
fdict = {}
lastFunction = 'NULL'
verbose = 0
baseID = 1000

messParamDict = {
    ('MPI_Allgather', 'sendcount'): 1,
    ('MPI_Allgather', 'sendtype'): 2,
    ('MPI_Allgatherv', 'sendcount'): 1,
    ('MPI_Allgatherv', 'sendtype'): 2,
    ('MPI_Allreduce', 'count'): 1,
    ('MPI_Allreduce', 'datatype'): 2,
    ('MPI_Alltoall', 'sendcount'): 1,
    ('MPI_Alltoall', 'sendtype'): 2,
    ('MPI_Bcast', 'count'): 1,
    ('MPI_Bcast', 'datatype'): 2,
    ('MPI_Bsend', 'count'): 1,
    ('MPI_Bsend', 'datatype'): 2,
    ('MPI_Gather', 'sendcnt'): 1,
    ('MPI_Gather', 'sendtype'): 2,
    ('MPI_Gatherv', 'sendcnt'): 1,
    ('MPI_Gatherv', 'sendtype'): 2,
    ('MPI_Ibsend', 'count'): 1,
    ('MPI_Ibsend', 'datatype'): 2,
    ('MPI_Irsend', 'count'): 1,
    ('MPI_Irsend', 'datatype'): 2,
    ('MPI_Isend', 'count'): 1,
    ('MPI_Isend', 'datatype'): 2,
    ('MPI_Issend', 'count'): 1,
    ('MPI_Issend', 'datatype'): 2,
    ('MPI_Reduce', 'count'): 1,
    ('MPI_Reduce', 'datatype'): 2,
    ('MPI_Rsend', 'count'): 1,
    ('MPI_Rsend', 'datatype'): 2,
    ('MPI_Scan', 'count'): 1,
    ('MPI_Scan', 'datatype'): 2,
    ('MPI_Scatter', 'sendcnt'): 1,
    ('MPI_Scatter', 'sendtype'): 2,
    ('MPI_Send', 'count'): 1,
    ('MPI_Send', 'datatype'): 2,
    ('MPI_Sendrecv', 'sendcount'): 1,
    ('MPI_Sendrecv', 'sendtype'): 2,
    ('MPI_Sendrecv_replace', 'count'): 1,
    ('MPI_Sendrecv_replace', 'datatype'): 2,
    ('MPI_Ssend', 'count'): 1,
    ('MPI_Ssend', 'datatype'): 2,
    }

ioParamDict = {
    ('MPI_File_read', 'count'): 1,
    ('MPI_File_read', 'datatype'): 2,
    ('MPI_File_read_all', 'count'): 1,
    ('MPI_File_read_all', 'datatype'): 2,
    ('MPI_File_read_at', 'count'): 1,
    ('MPI_File_read_at', 'datatype'): 2,
    ('MPI_File_write', 'count'): 1,
    ('MPI_File_write', 'datatype'): 2,
    ('MPI_File_write_all', 'count'): 1,
    ('MPI_File_write_all', 'datatype'): 2,
    ('MPI_File_write_at', 'count'): 1,
    ('MPI_File_write_at', 'datatype'): 2,
    }

rmaParamDict = {
    ('MPI_Accumulate', 'target_count'): 1,
    ('MPI_Accumulate', 'target_datatype'): 2,
    ('MPI_Get', 'origin_count'): 1,
    ('MPI_Get', 'origin_datatype'): 2,
    ('MPI_Put', 'origin_count'): 1,
    ('MPI_Put', 'origin_datatype'): 2,
    }

noDefineList = ['MPI_Pcontrol']

opaqueInArgDict = {
    ('MPI_Abort', 'comm'): 'MPI_Comm',
    ('MPI_Accumulate', 'origin_datatype'): 'MPI_Datatype',
    ('MPI_Accumulate', 'target_datatype'): 'MPI_Datatype',
    ('MPI_Accumulate', 'op'): 'MPI_Op',
    ('MPI_Accumulate', 'win'): 'MPI_Win',
    ('MPI_Add_error_string', 'string'): 'char_p',
    ('MPI_Allgather', 'comm'): 'MPI_Comm',
    ('MPI_Allgather', 'recvtype'): 'MPI_Datatype',
    ('MPI_Allgather', 'sendtype'): 'MPI_Datatype',
    ('MPI_Allgatherv', 'comm'): 'MPI_Comm',
    ('MPI_Allgatherv', 'recvtype'): 'MPI_Datatype',
    ('MPI_Allgatherv', 'sendtype'): 'MPI_Datatype',
    ('MPI_Allreduce', 'comm'): 'MPI_Comm',
    ('MPI_Allreduce', 'datatype'): 'MPI_Datatype',
    ('MPI_Allreduce', 'op'): 'MPI_Op',
    ('MPI_Alltoall', 'comm'): 'MPI_Comm',
    ('MPI_Alltoall', 'recvtype'): 'MPI_Datatype',
    ('MPI_Alltoall', 'sendtype'): 'MPI_Datatype',
    ('MPI_Alltoallv', 'comm'): 'MPI_Comm',
    ('MPI_Alltoallv', 'recvtype'): 'MPI_Datatype',
    ('MPI_Alltoallv', 'sendtype'): 'MPI_Datatype',
    ('MPI_Attr_delete', 'comm'): 'MPI_Comm',
    ('MPI_Attr_get', 'comm'): 'MPI_Comm',
    ('MPI_Attr_put', 'comm'): 'MPI_Comm',
    ('MPI_Attr_put', 'comm'): 'MPI_Comm',
    ('MPI_Barrier', 'comm'): 'MPI_Comm',
    ('MPI_Bcast', 'datatype'): 'MPI_Datatype',
    ('MPI_Bcast', 'comm'): 'MPI_Comm',
    ('MPI_Bsend', 'comm'): 'MPI_Comm',
    ('MPI_Bsend', 'datatype'): 'MPI_Datatype',
    ('MPI_Bsend_init', 'comm'): 'MPI_Comm',
    ('MPI_Bsend_init', 'datatype'): 'MPI_Datatype',
    ('MPI_Cancel', 'request'): 'MPI_Request',
    ('MPI_Cart_coords', 'comm'): 'MPI_Comm',
    ('MPI_Cart_create', 'comm_old'): 'MPI_Comm',
    ('MPI_Cart_get', 'comm'): 'MPI_Comm',
    ('MPI_Cart_map', 'comm_old'): 'MPI_Comm',
    ('MPI_Cart_rank', 'comm'): 'MPI_Comm',
    ('MPI_Cart_shift', 'comm'): 'MPI_Comm',
    ('MPI_Cart_sub', 'comm'): 'MPI_Comm',
    ('MPI_Cartdim_get', 'comm'): 'MPI_Comm',
    ('MPI_Comm_compare', 'comm1'): 'MPI_Comm',
    ('MPI_Comm_compare', 'comm2'): 'MPI_Comm',
    ('MPI_Comm_create', 'comm'): 'MPI_Comm',
    ('MPI_Comm_create', 'group'): 'MPI_Group',
    ('MPI_Comm_dup', 'comm'): 'MPI_Comm',
    ('MPI_Comm_free', 'commp'): 'MPI_Comm',
    ('MPI_Comm_group', 'comm'): 'MPI_Comm',
    ('MPI_Comm_rank', 'comm'): 'MPI_Comm',
    ('MPI_Comm_remote_group', 'comm'): 'MPI_Comm',
    ('MPI_Comm_remote_size', 'comm'): 'MPI_Comm',
    ('MPI_Comm_size', 'comm'): 'MPI_Comm',
    ('MPI_Comm_set_name', 'comm_name'): 'char_p',
    ('MPI_Comm_split', 'comm'): 'MPI_Comm',
    ('MPI_Comm_test_inter', 'comm'): 'MPI_Comm',
    ('MPI_Errhandler_get', 'comm'): 'MPI_Comm',
    ('MPI_Errhandler_set', 'comm'): 'MPI_Comm',
    ('MPI_File_close', 'fh'): 'MPI_File',
    ('MPI_File_delete', 'filename'): 'char_p',
    ('MPI_File_delete', 'info'): 'MPI_Info',
    ('MPI_File_open', 'comm'): 'MPI_Comm',
    ('MPI_File_open', 'info'): 'MPI_Info',
    ('MPI_File_open', 'filename'): 'char_p',
    ('MPI_File_preallocate', 'fh'): 'MPI_File',
    ('MPI_File_read', 'fh'): 'MPI_File',
    ('MPI_File_read', 'datatype'): 'MPI_Datatype',
    ('MPI_File_read_all', 'fh'): 'MPI_File',
    ('MPI_File_read_all', 'datatype'): 'MPI_Datatype',
    ('MPI_File_read_at', 'fh'): 'MPI_File',
    ('MPI_File_read_at', 'datatype'): 'MPI_Datatype',
    ('MPI_File_seek', 'fh'): 'MPI_File',
    ('MPI_File_set_view', 'fh'): 'MPI_File',
    ('MPI_File_set_view', 'etype'): 'MPI_Datatype',
    ('MPI_File_set_view', 'filetype'): 'MPI_Datatype',
    ('MPI_File_set_view', 'datarep'): 'char_p',
    ('MPI_File_set_view', 'info'): 'MPI_Info',
    ('MPI_File_write', 'fh'): 'MPI_File',
    ('MPI_File_write', 'datatype'): 'MPI_Datatype',
    ('MPI_File_write_all', 'fh'): 'MPI_File',
    ('MPI_File_write_all', 'datatype'): 'MPI_Datatype',
    ('MPI_File_write_at', 'fh'): 'MPI_File',
    ('MPI_File_write_at', 'datatype'): 'MPI_Datatype',
    ('MPI_Gather', 'comm'): 'MPI_Comm',
    ('MPI_Gather', 'recvtype'): 'MPI_Datatype',
    ('MPI_Gather', 'sendtype'): 'MPI_Datatype',
    ('MPI_Gatherv', 'comm'): 'MPI_Comm',
    ('MPI_Gatherv', 'recvtype'): 'MPI_Datatype',
    ('MPI_Gatherv', 'sendtype'): 'MPI_Datatype',
    ('MPI_Get', 'origin_datatype'): 'MPI_Datatype',
    ('MPI_Get', 'target_datatype'): 'MPI_Datatype',
    ('MPI_Get', 'win'): 'MPI_Win',
    ('MPI_Get_count', 'datatype'): 'MPI_Datatype',
    ('MPI_Get_count', 'status'): 'MPI_Status',
    ('MPI_Get_elements', 'datatype'): 'MPI_Datatype',
    ('MPI_Get_elements', 'status'): 'MPI_Status',
    ('MPI_Graph_create', 'comm_old'): 'MPI_Comm',
    ('MPI_Graph_get', 'comm'): 'MPI_Comm',
    ('MPI_Graph_map', 'comm_old'): 'MPI_Comm',
    ('MPI_Graph_neighbors', 'comm'): 'MPI_Comm',
    ('MPI_Graph_neighbors_count', 'comm'): 'MPI_Comm',
    ('MPI_Graphdims_get', 'comm'): 'MPI_Comm',
    ('MPI_Group_compare', 'group1'): 'MPI_Group',
    ('MPI_Group_compare', 'group2'): 'MPI_Group',
    ('MPI_Group_difference', 'group1'): 'MPI_Group',
    ('MPI_Group_difference', 'group2'): 'MPI_Group',
    ('MPI_Group_excl', 'group'): 'MPI_Group',
    ('MPI_Group_free', 'group'): 'MPI_Group',
    ('MPI_Group_incl', 'group'): 'MPI_Group',
    ('MPI_Group_intersection', 'group1'): 'MPI_Group',
    ('MPI_Group_intersection', 'group2'): 'MPI_Group',
    ('MPI_Group_range_excl', 'group'): 'MPI_Group',
    ('MPI_Group_range_incl', 'group'): 'MPI_Group',
    ('MPI_Group_rank', 'group'): 'MPI_Group',
    ('MPI_Group_size', 'group'): 'MPI_Group',
    ('MPI_Group_translate_ranks', 'group_a'): 'MPI_Group',
    ('MPI_Group_translate_ranks', 'group_b'): 'MPI_Group',
    ('MPI_Group_union', 'group1'): 'MPI_Group',
    ('MPI_Group_union', 'group2'): 'MPI_Group',
    ('MPI_Ibsend', 'comm'): 'MPI_Comm',
    ('MPI_Ibsend', 'datatype'): 'MPI_Datatype',
    ('MPI_Intercomm_create', 'local_comm'): 'MPI_Comm',
    ('MPI_Intercomm_create', 'peer_comm'): 'MPI_Comm',
    ('MPI_Intercomm_merge', 'comm'): 'MPI_Comm',
    ('MPI_Info_delete', 'key'): 'char_p',
    ('MPI_Info_get', 'key'): 'char_p',
    ('MPI_Info_get_veluelen', 'key'): 'char_p',
    ('MPI_Info_set', 'key'): 'char_p',
    ('MPI_Info_set', 'value'): 'char_p',
    ('MPI_Iprobe', 'comm'): 'MPI_Comm',
    ('MPI_Irecv', 'comm'): 'MPI_Comm',
    ('MPI_Irecv', 'datatype'): 'MPI_Datatype',
    ('MPI_Irsend', 'comm'): 'MPI_Comm',
    ('MPI_Irsend', 'datatype'): 'MPI_Datatype',
    ('MPI_Isend', 'comm'): 'MPI_Comm',
    ('MPI_Isend', 'datatype'): 'MPI_Datatype',
    ('MPI_Issend', 'comm'): 'MPI_Comm',
    ('MPI_Issend', 'datatype'): 'MPI_Datatype',
    ('MPI_Lookup_name', 'service_name'): 'char_p',
    ('MPI_Op_create', 'op'): 'MPI_Op',
    ('MPI_Pack', 'comm'): 'MPI_Comm',
    ('MPI_Pack', 'datatype'): 'MPI_Datatype',
    ('MPI_Pack_external', 'datarep'): 'char_p',
    ('MPI_Pack_external_size', 'datarep'): 'char_p',
    ('MPI_Pack_size', 'comm'): 'MPI_Comm',
    ('MPI_Pack_size', 'datatype'): 'MPI_Datatype',
    ('MPI_Probe', 'comm'): 'MPI_Comm',
    ('MPI_Put', 'origin_datatype'): 'MPI_Datatype',
    ('MPI_Put', 'target_datatype'): 'MPI_Datatype',
    ('MPI_Put', 'win'): 'MPI_Win',
    ('MPI_Recv', 'comm'): 'MPI_Comm',
    ('MPI_Recv', 'datatype'): 'MPI_Datatype',
    ('MPI_Recv_init', 'comm'): 'MPI_Comm',
    ('MPI_Recv_init', 'datatype'): 'MPI_Datatype',
    ('MPI_Register_datarep', 'datarep'): 'char_p',
    ('MPI_Reduce', 'comm'): 'MPI_Comm',
    ('MPI_Reduce', 'datatype'): 'MPI_Datatype',
    ('MPI_Reduce', 'op'): 'MPI_Op',
    ('MPI_Reduce_scatter', 'comm'): 'MPI_Comm',
    ('MPI_Reduce_scatter', 'datatype'): 'MPI_Datatype',
    ('MPI_Reduce_scatter', 'op'): 'MPI_Op',
    ('MPI_Request_free', 'request'): 'MPI_Request',
    ('MPI_Rsend', 'comm'): 'MPI_Comm',
    ('MPI_Rsend', 'datatype'): 'MPI_Datatype',
    ('MPI_Rsend_init', 'comm'): 'MPI_Comm',
    ('MPI_Rsend_init', 'datatype'): 'MPI_Datatype',
    ('MPI_Scan', 'comm'): 'MPI_Comm',
    ('MPI_Scan', 'op'): 'MPI_Op',
    ('MPI_Scan', 'datatype'): 'MPI_Datatype',
    ('MPI_Scatter', 'comm'): 'MPI_Comm',
    ('MPI_Scatter', 'recvtype'): 'MPI_Datatype',
    ('MPI_Scatter', 'sendtype'): 'MPI_Datatype',
    ('MPI_Scatterv', 'comm'): 'MPI_Comm',
    ('MPI_Scatterv', 'recvtype'): 'MPI_Datatype',
    ('MPI_Scatterv', 'sendtype'): 'MPI_Datatype',
    ('MPI_Send', 'comm'): 'MPI_Comm',
    ('MPI_Send', 'datatype'): 'MPI_Datatype',
    ('MPI_Send_init', 'comm'): 'MPI_Comm',
    ('MPI_Send_init', 'datatype'): 'MPI_Datatype',
    ('MPI_Sendrecv', 'comm'): 'MPI_Comm',
    ('MPI_Sendrecv', 'recvtag'): 'MPI_Datatype',
    ('MPI_Sendrecv', 'recvtype'): 'MPI_Datatype',
    ('MPI_Sendrecv', 'sendtype'): 'MPI_Datatype',
    ('MPI_Sendrecv_replace', 'comm'): 'MPI_Comm',
    ('MPI_Sendrecv_replace', 'datatype'): 'MPI_Datatype',
    ('MPI_Ssend', 'comm'): 'MPI_Comm',
    ('MPI_Ssend', 'datatype'): 'MPI_Datatype',
    ('MPI_Ssend_init', 'comm'): 'MPI_Comm',
    ('MPI_Ssend_init', 'datatype'): 'MPI_Datatype',
    ('MPI_Start', 'request'): 'MPI_Request',
    ('MPI_Startall', 'array_of_requests'): 'MPI_Request',
    ('MPI_Test', 'request'): 'MPI_Request',
    ('MPI_Test_cancelled', 'status'): 'MPI_Status',
    ('MPI_Testall', 'array_of_requests'): 'MPI_Request',
    ('MPI_Testany', 'array_of_requests'): 'MPI_Request',
    ('MPI_Testsome', 'array_of_requests'): 'MPI_Request',
    ('MPI_Topo_test', 'comm'): 'MPI_Comm',
    ('MPI_Type_commit', 'datatype'): 'MPI_Datatype',
    ('MPI_Type_contiguous', 'old_type'): 'MPI_Datatype',
    ('MPI_Type_count', 'datatype'): 'MPI_Datatype',
    ('MPI_Type_create_darray', 'oldtype'): 'MPI_Datatype',
    ('MPI_Type_create_hindexed', 'old_type'): 'MPI_Datatype',
    ('MPI_Type_create_hvector', 'old_type'): 'MPI_Datatype',
    ('MPI_Type_create_indexed_block', 'old_type'): 'MPI_Datatype',
    ('MPI_Type_create_resized', 'oldtype'): 'MPI_Datatype',
    ('MPI_Type_create_struct', 'array_old_types'): 'MPI_Datatype',
    ('MPI_Type_create_subarray', 'oldtype'): 'MPI_Datatype',
    ('MPI_Type_dup', 'type'): 'MPI_Datatype',
    ('MPI_Type_extent', 'datatype'): 'MPI_Datatype',
    ('MPI_Type_get_extent', 'datatype'): 'MPI_Datatype',
    ('MPI_Type_free', 'datatype'): 'MPI_Datatype',
    ('MPI_Type_get_contents', 'datatype'): 'MPI_Datatype',
    ('MPI_Type_get_envelope', 'datatype'): 'MPI_Datatype',
    ('MPI_Type_hindexed', 'old_type'): 'MPI_Datatype',
    ('MPI_Type_hindexed', 'array_of_indices'): 'MPI_Aint',
    ('MPI_Type_hvector', 'old_type'): 'MPI_Datatype',
    ('MPI_Type_hvector', 'stride'): 'MPI_Aint',
    ('MPI_Type_indexed', 'old_type'): 'MPI_Datatype',
    ('MPI_Type_lb', 'datatype'): 'MPI_Datatype',
    ('MPI_Type_set_name', 'comm_name'): 'char_p',
    ('MPI_Type_size', 'datatype'): 'MPI_Datatype',
    ('MPI_Type_struct', 'array_old_types'): 'MPI_Datatype',
    ('MPI_Type_struct', 'array_of_indices'): 'MPI_Aint',
    ('MPI_Type_ub', 'datatype'): 'MPI_Datatype',
    ('MPI_Type_vector', 'old_type'): 'MPI_Datatype',
    ('MPI_Unpack', 'comm'): 'MPI_Comm',
    ('MPI_Unpack', 'datatype'): 'MPI_Datatype',
    ('MPI_Unpack_external', 'datarep'): 'char_p',
    ('MPI_Wait', 'request'): 'MPI_Request',
    ('MPI_Waitall', 'array_of_requests'): 'MPI_Request',
    ('MPI_Waitany', 'array_of_requests'): 'MPI_Request',
    ('MPI_Waitsome', 'array_of_requests'): 'MPI_Request',
    ('MPI_Win_complete', 'win'): 'MPI_Win',
    ('MPI_Win_create', 'info'): 'MPI_Info',
    ('MPI_Win_create', 'comm'): 'MPI_Comm',
    ('MPI_Win_create', 'win'): 'MPI_Win',
    ('MPI_Win_fence', 'win'): 'MPI_Win',
    ('MPI_Win_free', 'win'): 'MPI_Win',
    ('MPI_Win_get_group', 'win'): 'MPI_Win',
    ('MPI_Win_get_group', 'group'): 'MPI_Group',
    ('MPI_Win_lock', 'win'): 'MPI_Win',
    ('MPI_Win_post', 'group'): 'MPI_Group',
    ('MPI_Win_post', 'win'): 'MPI_Win',
    ('MPI_Win_set_name', 'comm_name'): 'char_p',
    ('MPI_Win_start', 'group'): 'MPI_Group',
    ('MPI_Win_start', 'win'): 'MPI_Win',
    ('MPI_Win_test', 'win'): 'MPI_Win',
    ('MPI_Win_unlock', 'win'): 'MPI_Win',
    ('MPI_Win_wait', 'win'): 'MPI_Win',
    }

opaqueOutArgDict = {
    ('MPI_Bsend_init', 'request'): 'MPI_Request',
    ('MPI_Cart_create', 'comm_cart'): 'MPI_Comm',
    ('MPI_Cart_sub', 'comm_new'): 'MPI_Comm',
    ('MPI_Comm_create', 'comm_out'): 'MPI_Comm',
    ('MPI_Comm_dup', 'comm_out'): 'MPI_Comm',
    ('MPI_Comm_free', 'commp'): 'MPI_Comm',
    ('MPI_Comm_get_name', 'comm_name'): 'char_p',
    ('MPI_Comm_group', 'group'): 'MPI_Group',
    ('MPI_Comm_remote_group', 'group'): 'MPI_Group',
    ('MPI_Comm_split', 'comm_out'): 'MPI_Comm',
    ('MPI_Error_string', 'string'): 'char_p',
    ('MPI_File_close', 'fh'): 'MPI_File',
    ('MPI_File_open', 'fh'): 'MPI_File',
    ('MPI_File_read', 'status'): 'MPI_Status',
    ('MPI_File_read_all', 'status'): 'MPI_Status',
    ('MPI_File_read_at', 'status'): 'MPI_Status',
    ('MPI_File_write', 'status'): 'MPI_Status',
    ('MPI_File_write_all', 'status'): 'MPI_Status',
    ('MPI_File_write_at', 'status'): 'MPI_Status',
    ('MPI_Get_processor_name', 'name'): 'char_p',
    ('MPI_Graph_create', 'comm_graph'): 'MPI_Comm',
    ('MPI_Group_difference', 'group_out'): 'MPI_Group',
    ('MPI_Group_excl', 'newgroup'): 'MPI_Group',
    ('MPI_Group_free', 'group'): 'MPI_Group',
    ('MPI_Group_incl', 'group_out'): 'MPI_Group',
    ('MPI_Group_intersection', 'group_out'): 'MPI_Group',
    ('MPI_Group_range_excl', 'newgroup'): 'MPI_Group',
    ('MPI_Group_range_incl', 'newgroup'): 'MPI_Group',
    ('MPI_Group_union', 'group_out'): 'MPI_Group',
    ('MPI_Ibsend', 'request'): 'MPI_Request',
    ('MPI_Info_get', 'value'): 'char_p',
    ('MPI_Info_get_nthkey', 'key'): 'char_p',
    ('MPI_Intercomm_create', 'comm_out'): 'MPI_Comm',
    ('MPI_Intercomm_merge', 'comm_out'): 'MPI_Comm',
    ('MPI_Iprobe', 'status'): 'MPI_Status',
    ('MPI_Irecv', 'request'): 'MPI_Request',
    ('MPI_Irsend', 'request'): 'MPI_Request',
    ('MPI_Isend', 'request'): 'MPI_Request',
    ('MPI_Issend', 'request'): 'MPI_Request',
    ('MPI_Op_create', 'op'): 'MPI_Op',
    ('MPI_Op_free', 'op'): 'MPI_Op',
    ('MPI_Probe', 'status'): 'MPI_Status',
    ('MPI_Recv', 'status'): 'MPI_Status',
    ('MPI_Recv_init', 'request'): 'MPI_Request',
    ('MPI_Request_free', 'request'): 'MPI_Request',
    ('MPI_Rsend_init', 'request'): 'MPI_Request',
    ('MPI_Send_init', 'request'): 'MPI_Request',
    ('MPI_Sendrecv', 'status'): 'MPI_Status',
    ('MPI_Sendrecv_replace', 'status'): 'MPI_Status',
    ('MPI_Ssend_init', 'request'): 'MPI_Request',
    ('MPI_Start', 'request'): 'MPI_Request',
    ('MPI_Startall', 'array_of_requests'): 'MPI_Request',
    ('MPI_Test', 'request'): 'MPI_Request',
    ('MPI_Test', 'status'): 'MPI_Status',
    ('MPI_Testall', 'array_of_requests'): 'MPI_Request',
    ('MPI_Testall', 'array_of_statuses'): 'MPI_Status',
    ('MPI_Testany', 'array_of_requests'): 'MPI_Request',
    ('MPI_Testany', 'status'): 'MPI_Status',
    ('MPI_Testsome', 'array_of_requests'): 'MPI_Request',
    ('MPI_Testsome', 'array_of_statuses'): 'MPI_Status',
    ('MPI_Type_commit', 'datatype'): 'MPI_Datatype',
    ('MPI_Type_contiguous', 'newtype'): 'MPI_Datatype',
    ('MPI_Type_create_darray', 'newtype'): 'MPI_Datatype',
    ('MPI_Type_create_f90_complex', 'newtype'): 'MPI_Datatype',
    ('MPI_Type_create_f90_integer', 'newtype'): 'MPI_Datatype',
    ('MPI_Type_create_f90_real', 'newtype'): 'MPI_Datatype',
    ('MPI_Type_create_hindexed', 'newtype'): 'MPI_Datatype',
    ('MPI_Type_create_hvector', 'newtype'): 'MPI_Datatype',
    ('MPI_Type_create_indexed_block', 'newtype'): 'MPI_Datatype',
    ('MPI_Type_create_resized', 'newtype'): 'MPI_Datatype',
    ('MPI_Type_create_struct', 'newtype'): 'MPI_Datatype',
    ('MPI_Type_create_subarray', 'newtype'): 'MPI_Datatype',
    ('MPI_Type_dup', 'newtype'): 'MPI_Datatype',
    ('MPI_Type_extent', 'extent'): 'MPI_Aint',
    ('MPI_Type_free', 'datatype'): 'MPI_Datatype',
    ('MPI_Type_get_contents', 'array_of_datatypes'): 'MPI_Datatype',
    ('MPI_Type_get_name', 'comm_name'): 'char_p',
    ('MPI_Type_hindexed', 'newtype'): 'MPI_Datatype',
    ('MPI_Type_hvector', 'newtype'): 'MPI_Datatype',
    ('MPI_Type_indexed', 'newtype'): 'MPI_Datatype',
    ('MPI_Type_struct', 'newtype'): 'MPI_Datatype',
    ('MPI_Type_vector', 'newtype'): 'MPI_Datatype',
    ('MPI_Wait', 'request'): 'MPI_Request',
    ('MPI_Wait', 'status'): 'MPI_Status',
    ('MPI_Waitall', 'array_of_requests'): 'MPI_Request',
    ('MPI_Waitall', 'array_of_statuses'): 'MPI_Status',
    ('MPI_Waitany', 'array_of_requests'): 'MPI_Request',
    ('MPI_Waitany', 'status'): 'MPI_Status',
    ('MPI_Waitsome', 'array_of_requests'): 'MPI_Request',
    ('MPI_Waitsome', 'array_of_statuses'): 'MPI_Status',
    ('MPI_Win_get_name', 'comm_name'): 'char_p',
    }

incrementFortranIndexDict = {
    'MPI_Testany': ('*index', 1),
    'MPI_Testsome': ('array_of_indices', '*count'),
    'MPI_Waitany': ('*index', 1),
    'MPI_Waitsome': ('array_of_indices', '*count'),
    }

xlateFortranArrayExceptions = {('MPI_Testany', 'array_of_requests'
                               ): 'index', ('MPI_Waitany',
                               'array_of_requests'): 'index'}


class VarDesc:

    def __init__(
        self,
        name,
        basetype,
        pointerLevel,
        arrayLevel,
        ):
        '''initialize a new variable description structure'''

        self.name = name
        self.basetype = basetype
        self.pointerLevel = pointerLevel
        self.arrayLevel = arrayLevel
        self.recordIt = 0


class fdecl:

    def __init__(
        self,
        name,
        id,
        returntype,
        paramList,
        protoline,
        ):
        '''initialize a new function declaration structure'''

        self.name = name
        self.id = id
        self.returntype = returntype
        self.paramList = paramList
        self.paramDict = {}
        self.protoline = protoline
        self.wrapperPreList = []
        self.wrapperPostList = []
        self.nowrapper = 0
        self.paramConciseList = []
        self.extrafields = {}
        self.extrafieldsList = []
        self.sendCountPname = ''
        self.sendTypePname = ''
        self.recvCountPname = ''
        self.recvTypePname = ''
        self.ioCountPname = ''
        self.ioTypePname = ''
        self.rmaCountPname = ''
        self.rmaTypePname = ''


class xlateEntry:

    def __init__(self, mpiType, varName):
        '''initialize a new Fortran translation structure'''

        self.mpiType = mpiType
        self.varName = varName


def ProcessDirectiveLine(lastFunction, line):
    tokens = string.split(line)
    if tokens[0] == 'nowrapper':
        fdict[lastFunction].nowrapper = 1
    elif tokens[0] == 'extrafield':
        fdict[lastFunction].extrafieldsList.append(tokens[2])
        fdict[lastFunction].extrafields[tokens[2]] = tokens[1]
    else:
        print 'Warning: ', lastFunction, ' unknown directive [', \
            string.strip(line), ']'


def ProcessWrapperPreLine(lastFunction, line):

    # print "Processing wrapper pre [",string.strip(line),"] for ",lastFunction

    fdict[lastFunction].wrapperPreList.append(line)


def ProcessWrapperPostLine(lastFunction, line):

    # print "Processing wrapper post [",string.strip(line),"] for ",lastFunction

    fdict[lastFunction].wrapperPostList.append(line)


def DumpDict():
    for i in flist:
        print i
        if verbose:
            print '\tParams\t', fdict[i].paramList
            if fdict[i].wrapperPreList:
                print '\tpre\t', fdict[i].wrapperPreList
            if fdict[i].wrapperPostList:
                print '\tpost\t', fdict[i].wrapperPostList


#####
##### Some MPI types we want to record. If there are pointers to them, deref them.
##### To simplify, assume that the value can be an 'int' for printing and assignment.
#####

def SpecialParamRecord(funct, param):
    global flist
    global fdict
    basetype = fdict[funct].paramDict[param].basetype
    pointerLevel = fdict[funct].paramDict[param].pointerLevel
    arrayLevel = fdict[funct].paramDict[param].arrayLevel

    simplePointer = pointerLevel == 1 and arrayLevel == 0

    if basetype == 'MPI_Request' and simplePointer:
        return 1
    elif basetype == 'MPI_Comm' and simplePointer:
        return 1
    elif basetype == 'MPI_Datatype' and simplePointer:
        return 1
    elif basetype == 'MPI_Group' and simplePointer:
        return 1
    elif basetype == 'MPI_Info' and simplePointer:
        return 1
    elif basetype == 'int' and simplePointer:
        return 1
    else:
        return 0


#####
##### ParamDictUpdate - updates the datastructures for a function after
#####    the basics have been entered. Must be called for each function.
#####

def ParamDictUpdate(fname):
    global flist
    global fdict
    global messParamDict
    global ioParamDict
    global rmaParamDict
    for p in fdict[fname].paramList:

        # # check for pointers, arrays

        pname = 'NULL'
        basetype = 'NULL'
        pointerLevel = string.count(p, '*')
        arrayLevel = string.count(p, '[')
        if pointerLevel > 0 and arrayLevel > 0:

            # # handle pointers and arrays

            pname = p[string.rfind(p, '*') + 1:string.find(p, '[')]
            basetype = p[0:string.find(p, '*')]
        elif pointerLevel > 0:

            # # handle pointers

            pname = p[string.rfind(p, '*') + 1:len(p)]
            basetype = p[0:string.find(p, '*')]
        elif arrayLevel > 0:

            # # handle arrays

            pname = p[string.find(p, ' '):string.find(p, '[')]
            basetype = p[0:string.find(p, ' ')]
        else:

            # # normal hopefully :)

            tokens = string.split(p)
            if len(tokens) == 1:

                # # must be void

                pname = ''
                basetype = 'void'
            else:
                pname = string.strip(tokens[1])
                basetype = string.strip(tokens[0])

        pname = string.strip(pname)
        basetype = string.strip(basetype)
        fdict[fname].paramDict[pname] = VarDesc(pname, basetype,
                pointerLevel, arrayLevel)
        fdict[fname].paramConciseList.append(pname)

        #  Identify and assign message size parameters

        if messParamDict.has_key((fname, pname)):
            paramMessType = messParamDict[(fname, pname)]
            if paramMessType == 1:
                fdict[fname].sendCountPname = pname
            elif paramMessType == 2:
                fdict[fname].sendTypePname = pname
            elif paramMessType == 3:
                fdict[fname].recvCountPname = pname
            elif paramMessType == 4:
                fdict[fname].recvTypePname = pname

        #  Identify and assign io size parameters

        if ioParamDict.has_key((fname, pname)):
            paramMessType = ioParamDict[(fname, pname)]
            if paramMessType == 1:
                fdict[fname].ioCountPname = pname
            elif paramMessType == 2:
                fdict[fname].ioTypePname = pname

        #  Identify and assign rma size parameters

        if rmaParamDict.has_key((fname, pname)):
            paramMessType = rmaParamDict[(fname, pname)]
            if paramMessType == 1:
                fdict[fname].rmaCountPname = pname
            elif paramMessType == 2:
                fdict[fname].rmaTypePname = pname

        if fdict[fname].paramDict[pname].pointerLevel == 0 \
            and fdict[fname].paramDict[pname].arrayLevel == 0 \
            and fdict[fname].paramDict[pname].basetype != 'void':
            fdict[fname].paramDict[pname].recordIt = 1
        elif SpecialParamRecord(fname, pname):
            fdict[fname].paramDict[pname].recordIt = 1
        else:
            pass

        if verbose:

            # print "\t->",p

            print '\t', pname, basetype, pointerLevel, arrayLevel


#####
##### Parses the input file and loads the information into the function dict.
#####

def ReadInputFile(f):

    # parser states

    p_start = 'start'
    p_directives = 'directives'
    p_wrapper_pre = 'wrapper_pre'
    p_wrapper_post = 'wrapper_post'
    parserState = p_start
    global cnt
    global fdict
    global flist

    fcounter = baseID

    print '-----*----- Parsing input file'
    while 1:

        # #### read a line from input

        rawline = f.readline()
        if not rawline:
            break
        cnt = cnt + 1
        line = re.sub("\@.*$", '', rawline)

        # #### break it into tokens

        tokens = string.split(line)
        if not tokens:
            continue

        # #### determine what type of line this is and then parse it as required

        if string.find(line, '(') != -1 and string.find(line, ')') \
            != -1 and string.find(line, 'MPI_') != -1 and parserState \
            == p_start:

            # #### we have a prototype start line

            name = tokens[1]
            retype = tokens[0]
            lparen = string.index(line, '(')
            rparen = string.index(line, ')')
            paramstr = line[lparen + 1:rparen]
            paramList = map(string.strip, string.split(paramstr, ','))

            #    print cnt, "-->", name,  paramList

            fdict[name] = fdecl(name, fcounter, retype, paramList, line)
            if name not in noDefineList:
                fcounter = fcounter + 1
            ParamDictUpdate(name)
            lastFunction = name
            if verbose:
                print name
        else:

            # #### DIRECTIVES

            if tokens[0] == 'directives' and parserState \
                != p_directives:

                # #### beginning of directives

                parserState = p_directives
            elif tokens[0] == 'directives' and parserState \
                == p_directives:

                # #### end of directives

                parserState = p_start
            elif parserState == p_directives:

                # #### must be a directive, process it

                ProcessDirectiveLine(lastFunction, line)
            elif tokens[0] == 'wrapper_pre' and parserState \
                != p_wrapper_pre:

            # #### CODE WRAPPER PRE
                # #### beginning of wrapper_pre

                parserState = p_wrapper_pre
            elif tokens[0] == 'wrapper_pre' and parserState \
                == p_wrapper_pre:

                # #### end of wrapper_pre

                parserState = p_start
            elif parserState == p_wrapper_pre:

                # #### must be a directive, process it

                ProcessWrapperPreLine(lastFunction, line)
            elif tokens[0] == 'wrapper_post' and parserState \
                != p_wrapper_post:

            # #### CODE WRAPPER POST
                # #### beginning of wrapper_post

                parserState = p_wrapper_post
            elif tokens[0] == 'wrapper_post' and parserState \
                == p_wrapper_post:

                # #### end of wrapper_post

                parserState = p_start
            elif parserState == p_wrapper_post:

                # #### must be a directive, process it

                ProcessWrapperPostLine(lastFunction, line)
            else:

            # #### UNKNOWN

                print 'Unknown input line ', cnt, ':', line,

    flist = fdict.keys()
    flist.sort()
    fcounter = baseID
    for f in flist:
        fdict[f].id = fcounter
        if f not in noDefineList:
            fcounter = fcounter + 1
    print '-----*----- Parsing completed: ', len(fdict), \
        ' functions found.'


###
### create a standard file header and return the init list
###

def StandardFileHeader(fname):
    olist = []
    olist.append('/* ' + fname + ' */\n')
    olist.append('/* DO NOT EDIT -- AUTOMATICALLY GENERATED! */\n')
    olist.append('/* Timestamp: ' + time.strftime('%d %B %Y %H:%M',
                 time.localtime(time.time())) + '  */\n')
    olist.append('/* Location: ' + socket.gethostname() + ' ' + os.name
                 + ' */\n')
    olist.append('/* Creator: ' + os.environ['LOGNAME'] + '  */\n')
    olist.append('\n')
    olist.append('\n')
    return olist


###
### Scan the lists of all functions and look for optimization
### opportunities (in space/speed).
###
### NOT USED
###

def ParameterOptimization():
    global flist
    global fdict

    # #### visit each function and update each functions parameter dictionary

    for funct in flist:
        if verbose:
            print funct
        ParamDictUpdate(funct)


###
### Create the structure files.
###

def GenerateStructureFile():
    global flist
    global fdict
    print '-----*----- Generating structure files'
    cwd = os.getcwd()
    os.chdir(cwd)
    sname = cwd + '/mpiPi_def.h'
    g = open(sname, 'w')
    olist = StandardFileHeader(sname)

    olist.append('\n')
    olist.append('#define mpiPi_BASE ' + str(baseID) + '\n')
    olist.append('\n')

    for funct in flist:
        if funct not in noDefineList:
            olist.append('#define mpiPi_' + funct + ' '
                         + str(fdict[funct].id) + '\n')

    olist.append('''

/* eof */
''')
    g.writelines(olist)
    g.close()


###
### Generate a lookup table where mpiP can grab variables and function pointers.
###

def GenerateLookup():
    global flist
    global fdict

    print '-----*----- Generating the lookup table'
    cwd = os.getcwd()
    os.chdir(cwd)
    sname = cwd + '/lookup.c'
    g = open(sname, 'w')
    olist = StandardFileHeader(sname)

    olist.append('#include "mpiPi.h"\n')
    olist.append('#include "mpiPi_def.h"\n')
    olist.append('\n')
    olist.append('\n')

    olist.append('mpiPi_lookup_t mpiPi_lookup [] = {\n')

    counter = 0
    for funct in flist:
        if funct not in noDefineList:
            if counter < len(flist) and counter > 0:
                olist.append(',\n')
            olist.append('\t{ mpiPi_' + funct)
            olist.append(', "' + funct + '"')
            olist.append('}')
            counter = counter + 1

    olist.append(''',
\t{0,NULL}};
''')

    olist.append('\n')
    olist.append('/* eof */\n')
    g.writelines(olist)
    g.close()


###
### Create a MPI wrapper for one function using the information in the function dict.
### First, generate a generic wrapper, and then the FORTRAN, C wrappers.
###

def CreateWrapper(funct, olist):
    global fdict
    global arch

    if fdict[funct].nowrapper:
        return

    if verbose:
        print 'Wrapping ', funct

    decl = '\n' + 'int rc;\n'

    olist.append('''


/* --------------- ''' + funct
                 + ' --------------- */\n')

    # ####
    # #### Fortran wrapper
    # ####

    # #### funct decl

    olist.append('''

extern void ''' + 'F77_' + string.upper(funct)
                 + '(')

    # ================================================================================
    # In the case where MPI_Fint and and opaque objects such as MPI_Request are not the same size,
    #   we want to use MPI conversion functions.
    #
    # The most obvious problem we have encountered is for MPI_Request objects,
    #   but Communicators, Group, Datatype, Op, and File are also possibily problems.
    #
    # There are two cases:
    #   1) A single argument needs to be translated.
    #   2) An array of objects needs to be allocated and translated.
    #      This only appears necessary for Request and Datatype
    #
    # The algorithm for processing Fortran wrapper functions is as follows:
    #   1.  Declare all C variable versions for Fortran arguments.
    #   2.  Allocate any arrays to be used.
    #   3.  Perform any necessary pre-call array and scalar xlation.
    #   4.  Make the function call with appropriate C variables.
    #   5.  Perform any necessary post-call array and scalar xlation.
    #   6.  Free any arrays.
    # ================================================================================

    # ##  Type translation information

    xlateVarName = ''
    xlateVarNames = []
    xlateTypes = []
    xlateCount = 0

    arglen = ''

    #  Input types to translate

    xlateTargetTypes = [
        'MPI_Comm',
        'MPI_Datatype',
        'MPI_File',
        'MPI_Aint',
        'MPI_Group',
        'MPI_Info',
        'MPI_Op',
        'MPI_Request',
        'MPI_Status',
        'char_p',
        ]

    freelist = []

    #  Iterate through the arguments for this function

    for i in fdict[funct].paramConciseList:
        xlateDone = 0
        opaqueFound = 0

        if funct == 'MPI_Buffer_detach' and i == 'bufferptr':
            xlateTypes.append(fdict[funct].paramDict[i].basetype)
            xlateVarNames.append(i)
            decl += xlateTypes[xlateCount] + ' *c_' \
                + xlateVarNames[xlateCount] + ' = NULL;\n'
            xlateCount += 1
        if doOpaqueXlate is True and fdict[funct].paramDict[i].basetype \
            in xlateTargetTypes:

            #  Verify that there is a Dictionary entry for translating this argument

            if opaqueInArgDict.has_key((funct, i)) \
                or opaqueOutArgDict.has_key((funct, i)):
                opaqueFound = 1

                # All Fortran opaque object are of type MPI_Fint

                currBasetype = 'MPI_Fint'
                if fdict[funct].paramDict[i].basetype == 'char_p':
                    currBasetype = 'char'

                #  Store variable name and type

                xlateTypes.append(fdict[funct].paramDict[i].basetype)
                xlateVarNames.append(i)

                #  Try to identify whether array or single value by whether "array" is in the variable name
                #  and add C declaration to declaration list.

                if xlateVarNames[xlateCount].count('array') > 0:
                    decl += xlateTypes[xlateCount] + ' *c_' \
                        + xlateVarNames[xlateCount] + ' = NULL;\n'
                else:
                    decl += xlateTypes[xlateCount] + ' c_' \
                        + xlateVarNames[xlateCount] + ';\n'
                    if xlateTypes[xlateCount] == 'MPI_Status':
                        decl += xlateTypes[xlateCount] + ' *c_' \
                            + xlateVarNames[xlateCount] + '_p=&c_' \
                            + xlateVarNames[xlateCount] + ';\n'

                xlateCount += 1
            elif fdict[funct].paramDict[i].basetype == 'MPI_Aint':

                #  Not translating this variable

                currBasetype = fdict[funct].paramDict[i].basetype
            else:
                print '*** Failed to find translation information for ' \
                    + funct + ':' + i + '\n'
        else:

            #  Not translating this variable

            currBasetype = fdict[funct].paramDict[i].basetype

        #  Add argument to function declaration

        olist.append(currBasetype + ' ')

        if fdict[funct].paramDict[i].pointerLevel == 0 \
            and fdict[funct].paramDict[i].arrayLevel == 0 \
            and fdict[funct].paramDict[i].basetype != 'void':
            olist.append(' * ')

        if fdict[funct].paramDict[i].pointerLevel > 0:
            for j in xrange(1, fdict[funct].paramDict[i].pointerLevel
                            + 1):
                olist.append(' *')

        olist.append(i)

        if fdict[funct].paramDict[i].basetype == 'char_p':
            arglen = ', int %s_len' % i

        if fdict[funct].paramDict[i].arrayLevel > 0:
            for x in range(0, fdict[funct].paramDict[i].arrayLevel):
                if x > 0:
                    olist.append('[3]')
                else:
                    olist.append('[]')
        if fdict[funct].paramConciseList.index(i) \
            < len(fdict[funct].paramConciseList) - 1:
            olist.append(', ')

    #  Add ierr argument and declarations to output list

    olist.append(' , MPI_Fint *ierr ' + arglen + ')')
    olist.append('{')
    olist.append(decl)
    olist.append('\n')

    if fdict[funct].wrapperPreList:
        olist.extend(fdict[funct].wrapperPreList)

    if 'mips' in arch:
        olist.append('/* For MIPS+GCC we get a single level of stack backtrace using an intrinsic */\n'
                     )
        olist.append('#if defined(mips) && defined (__GNUC__)\n')
        olist.append('  saved_ret_addr = __builtin_return_address(0);\n'
                     )
        olist.append('''#endif

''')
    else:
        if useSetJmp == True:
            olist.append('''setjmp (jbuf);

''')

    #  Allocate any arrays used for translation

    for i in range(len(xlateVarNames)):
        xlateVarName = xlateVarNames[i]
        xlateType = xlateTypes[i]

        #  A pretty sketchy way of identifying an array size, but as far as I can tell,
        #  only one array is passed as an argument per function.

        if fdict[funct].paramConciseList.count('count') > 1:
            print '*** Multiple arrays in 1 function!!!!\n'

        if 'incount' in fdict[funct].paramConciseList:
            countVar = 'incount'
        elif 'count' in fdict[funct].paramConciseList:
            countVar = 'count'
        else:
            countVar = 'max_integers'

        if xlateVarName.count('array') > 0:
            olist.append('if( *' + countVar + ' > 0)\n')
            olist.append('{\n')
            olist.append('c_' + xlateVarName + ' = (' + xlateType
                         + '*)malloc(sizeof(' + xlateType + ')*(*'
                         + countVar + '));\n')
            olist.append('}\n')
            olist.append('if ( c_' + xlateVarName
                         + ' == NULL ) { *ierr=MPI_ERROR_MEM; return; }\n'
                         )

            # olist.append("if ( c_" + xlateVarName + " == NULL ) mpiPi_abort(\"Failed to allocate memory in " \
                # + funct + "\");\n")

            freelist.append('c_' + xlateVarName)

        if xlateType == 'char_p':
            olist.append('c_' + xlateVarName + ' = (' + xlateType
                         + ')malloc(sizeof(' + xlateType + ')*('
                         + xlateVarName + '_len));\n')
            olist.append('if ( c_' + xlateVarName
                         + ' == NULL ) { *ierr=MPI_ERROR_MEM; return; }\n'
                         )

            # olist.append("if ( c_" + xlateVarName + " == NULL ) mpiPi_abort(\"Failed to allocate memory in " \
                # + funct + "\");\n")

            freelist.append('c_' + xlateVarName)

    #  Generate pre-call translation code if necessary by iterating through arguments that
    #  were identified as opaque objects needing translation above

    for i in range(len(xlateVarNames)):

        #  Set current argument name and type

        xlateVarName = xlateVarNames[i]
        xlateType = xlateTypes[i]

        #  Check for valid function:argument-name entry for pre-call translation.

        if opaqueInArgDict.has_key((funct, xlateVarName)) \
            and opaqueInArgDict[(funct, xlateVarName)] == xlateType:

            #  Datatype translation is the only call where the translation function
            #  doesn't match the argument type.

            if xlateType == 'MPI_Datatype':
                xlateFuncType = 'MPI_Type_f2c'
            elif xlateType == 'MPI_Aint':
                xlateFuncType = '(MPI_Aint)'
            else:
                xlateFuncType = xlateType + '_f2c'

            if xlateVarName.count('status') > 0:
                olist.append('#ifdef HAVE_MPI_STATUS_C2F\n')
                if xlateVarName.count('array') > 0:
                    olist.append('#ifdef HAVE_MPI_STATUSES_IGNORE\n')
                    olist.append('#ifdef HAVE_MPI_F_STATUSES_IGNORE\n')
                    olist.append('  if ( ' + xlateVarName
                                 + ' != MPI_F_STATUSES_IGNORE )\n')
                    olist.append('#endif //HAVE_MPI_F_STATUSES_IGNORE\n'
                                 )
                    olist.append('#endif //HAVE_MPI_STATUSES_IGNORE\n')
                    olist.append('''  {
  int i;
''')
                    olist.append('  for (i = 0; i < *' + countVar
                                 + '; i++) { \n')
                    olist.append('    MPI_Status_f2c(&(' + xlateVarName
                                 + '[i]),&(c_' + xlateVarName
                                 + '[i*PNMPI_F_STATUS_SIZE]));\n')
                    olist.append('''  }
}
''')
                else:
                    olist.append('#ifdef HAVE_MPI_STATUS_IGNORE\n')
                    olist.append('#ifdef HAVE_MPI_F_STATUS_IGNORE\n')
                    olist.append('  if ( ' + xlateVarName
                                 + ' != MPI_F_STATUS_IGNORE )\n')
                    olist.append('#endif //HAVE_MPI_F_STATUS_IGNORE\n')
                    olist.append('#endif //HAVE_MPI_STATUS_IGNORE\n')
                    olist.append('    { MPI_Status_f2c(' + xlateVarName
                                 + ',&c_' + xlateVarName + '); }\n')
                olist.append('#endif //HAVE_MPI_STATUS_C2F\n')
            elif xlateType == 'char_p':
                olist.append(xlateFuncType + '(' + xlateVarName + ', '
                             + xlateVarName + '_len, &c_'
                             + xlateVarName + ');\n')
            else:
                if xlateVarName.count('array') > 0:
                    olist.append('''  {
  int i;
''')
                    olist.append('  for (i = 0; i < *' + countVar
                                 + '; i++) { \n')
                    olist.append('    c_' + xlateVarName + '[i] = '
                                 + xlateFuncType + '(' + xlateVarName
                                 + '[i]);\n')
                    olist.append('''  }
}
''')
                else:
                    olist.append('c_' + xlateVarName + ' = '
                                 + xlateFuncType + '(*' + xlateVarName
                                 + ');\n')

            xlateDone = 1

        if xlateType == 'MPI_Status' \
            and opaqueOutArgDict.has_key((funct, xlateVarName)) \
            and opaqueOutArgDict[(funct, xlateVarName)] == xlateType:

            #  Generate array or scalar translation code

            if xlateVarName.count('array') > 0:
                olist.append('#ifdef HAVE_MPI_STATUSES_IGNORE\n')
                olist.append('#ifdef HAVE_MPI_F_STATUSES_IGNORE\n')
                olist.append('  if ( ' + xlateVarName
                             + ' == MPI_F_STATUSES_IGNORE )\n')
                olist.append('    { c_' + xlateVarName
                             + ' = MPI_STATUSES_IGNORE; }\n')
                olist.append('#endif //HAVE_MPI_F_STATUSES_IGNORE\n')
                olist.append('#endif //HAVE_MPI_STATUSES_IGNORE\n')
            else:
                olist.append('#ifdef HAVE_MPI_STATUS_IGNORE\n')
                olist.append('#ifdef HAVE_MPI_F_STATUS_IGNORE\n')
                olist.append('  if ( ' + xlateVarName
                             + ' == MPI_F_STATUS_IGNORE )\n')
                olist.append('    { c_' + xlateVarName
                             + '_p = MPI_STATUS_IGNORE; }\n')
                olist.append('#endif //HAVE_MPI_F_STATUS_IGNORE\n')
                olist.append('#endif //HAVE_MPI_STATUS_IGNORE\n')

    #  Start generating call to C/Fortran common mpiP wrapper function

    olist.append('\n' + 'DBGPRINT3("Entering Old Fortran ' + funct
                 + ' at base level");\n')

    olist.append('#ifdef ' + funct + '_ID\n')
    olist.append('\n' + 'if (NOT_ACTIVATED(' + funct
                 + '_ID) || pnmpi_mpi_level > 0)\n' + '{\n' + '  rc=P'
                 + funct + '( ')

    argname = ''

     # Iterate through mpiP wrapper function arguments, replacing argument with C version where appropriate

    for i in fdict[funct].paramConciseList:
        if i in xlateVarNames and (opaqueInArgDict.has_key((funct, i))
                                   or opaqueOutArgDict.has_key((funct,
                                   i)) or funct == 'MPI_Buffer_detach'):
            if i.count('array') > 0:
                argname = 'c_' + i
            elif i.count('status') > 0:
                argname = 'c_' + i + '_p'
            else:
                argname = '&c_' + i
        else:
            argname = i

        if fdict[funct].paramDict[i].pointerLevel == 0 \
            and fdict[funct].paramDict[i].arrayLevel == 0 \
            and fdict[funct].paramDict[i].basetype != 'void':
            olist.append(' * ' + argname)
        elif fdict[funct].paramDict[i].pointerLevel > 0:
            olist.append(argname)
        elif fdict[funct].paramDict[i].arrayLevel > 0:
            olist.append(argname)
        else:
            print 'Warning: passing on arg', i, 'in', funct
        if fdict[funct].paramConciseList.index(i) \
            < len(fdict[funct].paramConciseList) - 1:
            olist.append(', ')

    olist.append(''' );
}
''')
    olist.append('''else
{
''' + '  rc=Internal_X' + funct + '( ')

    if 'count' in fdict[funct].paramConciseList:
        countVar = 'count'
    elif 'incount' in fdict[funct].paramConciseList:
        countVar = 'incount'
    else:
        countVar = 'max_integers'

    #  Iterate through mpiP wrapper function arguments, replacing argument with C version where appropriate

    for i in fdict[funct].paramConciseList:
        if i in xlateVarNames and (opaqueInArgDict.has_key((funct, i))
                                   or opaqueOutArgDict.has_key((funct,
                                   i)) or funct == 'MPI_Buffer_detach'):
            if i.count('array') > 0:
                argname = 'c_' + i
            elif i.count('status') > 0:
                argname = 'c_' + i + '_p'
            else:
                argname = '&c_' + i
        else:
            argname = i

        if fdict[funct].paramDict[i].pointerLevel == 0 \
            and fdict[funct].paramDict[i].arrayLevel == 0 \
            and fdict[funct].paramDict[i].basetype != 'void':
            olist.append(' * ' + argname)
        elif fdict[funct].paramDict[i].pointerLevel > 0:
            olist.append(argname)
        elif fdict[funct].paramDict[i].arrayLevel > 0:
            olist.append(argname)
        else:
            print 'Warning: passing on arg', i, 'in', funct
        if fdict[funct].paramConciseList.index(i) \
            < len(fdict[funct].paramConciseList) - 1:
            olist.append(', ')

    olist.append(''' );
}

#else
  rc=0;
#endif //''' + funct + '_ID\n')
    olist.append('*ierr = (MPI_Fint)rc;\n')

    #  Generate post-call translation code if necessary

    xlateCode = []
    xlateDone = 0

    #  If appropriate, increment any output indices

    if incrementFortranIndexDict.has_key(funct):
        if incrementFortranIndexDict[funct][1] == 1:
            xlateCode.append('\n('
                             + incrementFortranIndexDict[funct][0]
                             + ')++;\n')
        else:
            xlateCode.append('''
{ int i;
 for ( i = 0; i < '''
                             + incrementFortranIndexDict[funct][1]
                             + '; i++) {\n    '
                             + incrementFortranIndexDict[funct][0]
                             + '''[i]++;
}}
''')
    for i in range(len(xlateVarNames)):

        xlateVarName = xlateVarNames[i]
        xlateType = xlateTypes[i]

        if opaqueOutArgDict.has_key((funct, xlateVarName)) \
            and opaqueOutArgDict[(funct, xlateVarName)] == xlateType:

            #  Datatype translation is the only call where the translation function
            #  doesn't match the argument type.

            if xlateType == 'MPI_Datatype':
                xlateFuncType = 'MPI_Type_c2f'
            elif xlateType == 'MPI_Aint':
                xlateFuncType = '(MPI_Fint)'
            else:
                xlateFuncType = xlateType + '_c2f'

            #  Generate array or scalar translation code

            if xlateVarName.count('status') > 0:
                xlateCode.append('#ifdef HAVE_MPI_STATUS_C2F\n')
                if xlateVarName.count('array') > 0:
                    xlateCode.append('#ifdef HAVE_MPI_STATUSES_IGNORE\n'
                            )
                    xlateCode.append('#ifdef HAVE_MPI_F_STATUSES_IGNORE\n'
                            )
                    xlateCode.append('  if ( ' + xlateVarName
                            + ' != MPI_F_STATUSES_IGNORE )\n')
                    xlateCode.append('#endif //HAVE_MPI_F_STATUSES_IGNORE\n'
                            )
                    xlateCode.append('#endif //HAVE_MPI_STATUSES_IGNORE\n'
                            )
                    xlateCode.append('''   {
  int i;
''')
                    xlateCode.append('      for (i = 0; i < *'
                            + countVar + '; i++) { \n')
                    xlateCode.append('         ' + xlateFuncType
                            + '(&(c_' + xlateVarName + '[i]),&('
                            + xlateVarName + '[i*PNMPI_F_STATUS_SIZE]));\n')
                    xlateCode.append('''   }
}
''')
                else:
                    xlateCode.append('#ifdef HAVE_MPI_STATUS_IGNORE\n')
                    xlateCode.append('#ifdef HAVE_MPI_F_STATUS_IGNORE\n'
                            )
                    xlateCode.append('  if ( ' + xlateVarName
                            + ' != MPI_F_STATUS_IGNORE )\n')
                    xlateCode.append('#endif //HAVE_MPI_F_STATUS_IGNORE\n'
                            )
                    xlateCode.append('#endif //HAVE_MPI_STATUS_IGNORE\n'
                            )
                    xlateCode.append('    { ' + xlateFuncType + '(&c_'
                            + xlateVarName + ',' + xlateVarName
                            + ');}\n')
                xlateCode.append('#endif //HAVE_MPI_STATUS_C2F\n')
            elif xlateType == 'char_p':
                olist.append(xlateFuncType + '(c_' + xlateVarName + ', '
                              + xlateVarName + ', ' + xlateVarName
                             + '_len);\n')
            else:
                if xlateFortranArrayExceptions.has_key((funct,
                        xlateVarName)):
                    xlateCode.append('if(*'
                            + xlateFortranArrayExceptions[(funct,
                            xlateVarName)] + ' >=0 && *'
                            + xlateFortranArrayExceptions[(funct,
                            xlateVarName)] + ' < *' + countVar + ')\n  '
                             + xlateVarName + '[*'
                            + xlateFortranArrayExceptions[(funct,
                            xlateVarName)] + '] = ' + xlateFuncType
                            + '(c_' + xlateVarName + '[*'
                            + xlateFortranArrayExceptions[(funct,
                            xlateVarName)] + ']);\n')
                elif xlateVarName.count('array') > 0:

                    xlateCode.append('''{
  int i;
''')
                    xlateCode.append('  for (i = 0; i < *' + countVar
                            + '; i++) { \n')

                    # TODO QUICK HACK, this is nothing half nor anything full, but it solves my issues for the time being
                    # # For the "some" calls we need to make sure to only convert the right requests

                    if funct == 'MPI_Waitsome' or funct \
                        == 'MPI_Testsome':
                        xlateCode.append('    ' + xlateVarName
                                + '[(array_of_indices[i])-1] = '
                                + xlateFuncType + '(c_' + xlateVarName
                                + '[(array_of_indices[i])-1]);\n')
                    else:
                        xlateCode.append('    ' + xlateVarName
                                + '[i] = ' + xlateFuncType + '(c_'
                                + xlateVarName + '[i]);\n')

                    # ENDTODO

                    xlateCode.append('''  }
}
''')
                else:
                    xlateCode.append('*' + xlateVarName + ' = '
                            + xlateFuncType + '(c_' + xlateVarName
                            + ');\n')

            xlateDone = 1

    if xlateDone == 1:
        olist.append('if ( rc == MPI_SUCCESS ) { \n')

      # print " xlateCode is ", xlateCode

        olist.extend(xlateCode)
        olist.append('}\n')

    #  Free allocated arrays

    for freeSym in freelist:
        olist.append('if (' + freeSym + ') free(' + freeSym + ');\n')

    olist.append('return;\n' + '}' + ' /* ' + string.lower(funct)
                 + ' */\n')

    if opaqueFound == 1 and xlateDone == 0:
        print 'Function ' + funct + ' not translated!\n'

    print '   Wrapped ' + funct


def GenerateWrappers():
    global flist
    global fdict
    global arch
    global doWeakSymbols

    print '-----*----- Generating profiling wrappers'
    cwd = os.getcwd()
    os.chdir(cwd)
    sname = cwd + '/wrapper_f77.c'
    g = open(sname, 'w')
    olist = StandardFileHeader(sname)
    olist.append('#include <mpi.h>\n')
    olist.append('#include "f77symbols.h"\n')
    olist.append('#include "core.h"\n')
    olist.append('#include "pnmpi-config.h"\n')
    if doWeakSymbols == True:
        olist.append('#include "weak-symbols.h"\n')

    olist.append('#include <string.h>\n')
    olist.append('#include <stdlib.h>\n')
    olist.append('''typedef char* char_p;

''')
    olist.append(r"""void char_p_f2c(const char* fstr, int len, char** cstr)
{
  const char* end;
  int i;

  /* Leading and trailing blanks are discarded. */

  end = fstr + len - 1;

  for (i = 0; (i < len) && (' ' == *fstr); ++i, ++fstr) {
    continue;
  }

  if (i >= len) {
    len = 0;
  } else {
    for (; (end > fstr) && (' ' == *end); --end) {
      continue;
    }

    len = end - fstr + 1;
  }

  /* Allocate space for the C string, if necessary. */

  if (*cstr == NULL) {
    if ((*cstr = malloc(len + 1)) == NULL) {
      return;
    }
  }

  /* Copy F77 string into C string and NULL terminate it. */

  if (len > 0) {
    strncpy(*cstr, fstr, len);
  }
  (*cstr)[len] = '\0';
}

void char_p_c2f(const char* cstr, char* fstr, int len)
{
  int i;

  strncpy(fstr, cstr, len);
  for (i = strnlen(cstr, len); i < len; ++i) {
    fstr[i] = ' ';
  }
}
    """
                 )
    olist.append('\n')

####
#### Handle MIPS+GCC specially by creating a variable to save the return address
####

    if 'mips' in arch:
        olist.append('#if defined(mips) && defined(__GNUC__)\n')
        olist.append('  void* saved_ret_addr;\n')
        olist.append('''#endif

''')

    for funct in flist:
        CreateWrapper(funct, olist)
    olist.append('\n')
    olist.append('\n')
    olist.append('/* eof */\n')
    g.writelines(olist)
    g.close()


def GetFortranSymbol(fsymtp, fsym):
    ofsym = ''

    if fsymtp == 'symbol':
        ofsym = string.lower(fsym)
    elif fsymtp == 'symbol_':
        ofsym = string.lower(fsym) + '_'
    elif fsymtp == 'symbol__':
        ofsym = string.lower(fsym) + '__'
    elif fsymtp == 'SYMBOL':
        ofsym = string.upper(fsym)
    elif fsymtp == 'SYMBOL_':
        ofsym = string.upper(fsym) + '_'
    elif fsymtp == 'SYMBOL__':
        ofsym = string.upper(fsym) + '__'

    return ofsym


def GenerateWeakSymbols():
    global flist
    global f77symbol

    #
    # Generate Weak Symbols
    #

    cwd = os.getcwd()
    os.chdir(cwd)
    sname = cwd + '/weak-symbols.h'
    g = open(sname, 'w')

    sname = cwd + '/weak-symbols-special.h'
    s = open(sname, 'w')

    sname = cwd + '/weak-symbols-pcontrol.h'
    p = open(sname, 'w')

    fmlist = [
        'symbol',
        'symbol_',
        'symbol__',
        'SYMBOL',
        'SYMBOL_',
        'SYMBOL__',
        ]
    if f77symbol in fmlist:
        fmlist.remove(f77symbol)

    symflist = copy.deepcopy(flist)

    for funct in symflist:
        dfunc = GetFortranSymbol(f77symbol, funct)

        for mt in fmlist:
            wfunc = GetFortranSymbol(mt, funct)
            if funct in ['MPI_Init', 'MPI_Init_thread', 'MPI_Finalize']:
                s.write('#pragma weak ' + wfunc + ' = ' + dfunc + '\n')
            elif 'Pcontrol' in funct:
                p.write('#pragma weak ' + wfunc + ' = ' + dfunc + '\n')
            elif fdict[funct].nowrapper == 0:
                g.write('#pragma weak ' + wfunc + ' = ' + dfunc + '\n')

    g.close()
    p.close()
    s.close()


def GenerateSymbolDefs():
    global flist
    global f77symbol

    cwd = os.getcwd()
    os.chdir(cwd)
    sname = cwd + '/f77symbols.h'

    symflist = copy.deepcopy(flist)
    symflist.append('mpipi_get_fortran_argc')
    symflist.append('mpipi_get_fortran_arg')

    g = open(sname, 'w')
    for funct in symflist:
        if f77symbol == 'symbol':
            f77funct = string.lower(funct)
        elif f77symbol == 'symbol_':
            f77funct = string.lower(funct) + '_'
        elif f77symbol == 'symbol__':
            f77funct = string.lower(funct) + '__'
        elif f77symbol == 'SYMBOL':
            f77funct = string.upper(funct)
        elif f77symbol == 'SYMBOL_':
            f77funct = string.upper(funct) + '_'
        elif f77symbol == 'SYMBOL__':
            f77funct = string.upper(funct) + '__'
        else:
            f77funct = string.lower(funct) + '_'

        g.write('#define F77_' + string.upper(funct) + ' ' + f77funct
                + '\n')

    g.close()


def main():
    global fdict
    global flist
    global f77symbol
    global doOpaqueXlate
    global arch
    global doWeakSymbols
    global useSetJmp

    (opts, pargs) = getopt.getopt(sys.argv[1:], '', ['f77symbol=',
                                  'xlate', 'arch=', 'weak', 'usesetjmp'
                                  ])

    print 'MPI Wrapper Generator ($Revision: 1.2 $)'

    # print "opts=",opts
    # print "pargs=",pargs

    f77symbol = 'symbol'
    doOpaqueXlate = False
    doWeakSymbols = False
    useSetJmp = False
    arch = 'unknown'

    for (o, a) in opts:
        if o == '--f77symbol':
            f77symbol = a
        if o == '--xlate':
            doOpaqueXlate = True
        if o == '--weak':
            doWeakSymbols = True
        if o == '--arch':
            arch = a
        if o == '--usesetjmp':
            useSetJmp = True

    # #### Load the input file

    if len(pargs) < 1:
        f = sys.__stdin__
    else:
        f = open(pargs[0])
    ReadInputFile(f)

    print '-----*----- Beginning parameter optimization'

    # ParameterOptimization()

    GenerateStructureFile()
    GenerateWrappers()
    GenerateSymbolDefs()
    if doWeakSymbols == True:
        GenerateWeakSymbols()
    GenerateLookup()


#####
##### Call main
#####

main()

#
#
#  <license>
#
#  Copyright (c) 2006, The Regents of the University of California.
#  Produced at the Lawrence Livermore National Laboratory
#  Written by Jeffery Vetter and Christopher Chambreau.
#  UCRL-CODE-223450.
#  All rights reserved.
#
#  This file is part of mpiP.  For details, see http://mpip.sourceforge.net/.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#  * Redistributions of source code must retain the above copyright
#  notice, this list of conditions and the disclaimer below.
#
#  * Redistributions in binary form must reproduce the above copyright
#  notice, this list of conditions and the disclaimer (as noted below) in
#  the documentation and/or other materials provided with the
#  distribution.
#
#  * Neither the name of the UC/LLNL nor the names of its contributors
#  may be used to endorse or promote products derived from this software
#  without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OF
#  THE UNIVERSITY OF CALIFORNIA, THE U.S. DEPARTMENT OF ENERGY OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#
#  Additional BSD Notice
#
#  1. This notice is required to be provided under our contract with the
#  U.S. Department of Energy (DOE).  This work was produced at the
#  University of California, Lawrence Livermore National Laboratory under
#  Contract No. W-7405-ENG-48 with the DOE.
#
#  2. Neither the United States Government nor the University of
#  California nor any of their employees, makes any warranty, express or
#  implied, or assumes any liability or responsibility for the accuracy,
#  completeness, or usefulness of any information, apparatus, product, or
#  process disclosed, or represents that its use would not infringe
#  privately-owned rights.
#
#  3.  Also, reference herein to any specific commercial products,
#  process, or services by trade name, trademark, manufacturer or
#  otherwise does not necessarily constitute or imply its endorsement,
#  recommendation, or favoring by the United States Government or the
#  University of California.  The views and opinions of authors expressed
#  herein do not necessarily state or reflect those of the United States
#  Government or the University of California, and shall not be used for
#  advertising or product endorsement purposes.
#
#  </license>
#
#
# --- EOF
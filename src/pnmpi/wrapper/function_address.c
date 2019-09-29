/* This file is part of P^nMPI.
 *
 * Copyright (c)
 *  2008-2017 Lawrence Livermore National Laboratories, United States of America
 *  2011-2017 ZIH, Technische Universitaet Dresden, Federal Republic of Germany
 *  2013-2017 RWTH Aachen University, Federal Republic of Germany
 *
 *
 * P^nMPI is free software; you can redistribute it and/or modify it under the
 * terms of the GNU Lesser General Public License as published by the Free
 * Software Foundation version 2.1 dated February 1999.
 *
 * P^nMPI is distributed in the hope that it will be useful, but WITHOUT ANY
 * WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
 * A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
 * details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with P^nMPI; if not, write to the
 *
 *   Free Software Foundation, Inc.
 *   51 Franklin St, Fifth Floor
 *   Boston, MA 02110, USA
 *
 *
 * Written by Martin Schulz, schulzm@llnl.gov.
 *
 * LLNL-CODE-402774
 */

#include <pnmpi/private/attributes.h>
#include <pnmpi/private/function_address.h>


/** \brief The current MPI function address.
 *
 * \details This variable stores the application's return address. With
 *  additional tools like `addr2line` this address may be translated into the
 *  position in the source-code, where the application called the MPI call, e.g.
 *  to print warnings to the user.
 *
 * \note This value should not be changed directly by any function, but by using
 *  the \ref pnmpi_function_address_set and \ref pnmpi_function_address_reset
 *  functions.
 *
 *
 * \private
 */
PNMPI_INTERNAL
pnmpi_compiler_tls_keyword void *pnmpi_function_address = NULL;
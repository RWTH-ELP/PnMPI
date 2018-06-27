/* This file is part of P^nMPI.
 *
 * Copyright (c)
 *  2008-2018 Lawrence Livermore National Laboratories, United States of America
 *  2011-2016 ZIH, Technische Universitaet Dresden, Federal Republic of Germany
 *  2013-2018 RWTH Aachen University, Federal Republic of Germany
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

#include "core.h"
#include <pnmpi/private/attributes.h>
#include <pnmpi/wrapper.h>

/**
 * Global counter for number of initializations.
 *
 * This counter will be increased on any call to the initialization functions
 * and decreased on finalization. It ensures PnMPI is initialized only once and
 * finalized in the last finalization call.
 *
 *
 * @private
 */
PNMPI_INTERNAL
int pnmpi_initialized = 0;


/**
 * Initialize PnMPI.
 *
 * This function initializes PnMPI, if it isn't already. All wrappers should
 * call this function in their entry point function (i.e. the function of the
 * wrapped library applications should call first like `MPI_Init` for MPI).
 *
 * @note This function must be called before using any of PnMPI's functions.
 */
void PnMPI_Init(void)
{
  /* If PnMPI is already initialized, do not initialize it twice. In addition,
   * an internal counter tracks, how often the this function is called, so PnMPI
   * (especially its finalization function) know, how many wrappers of PnMPI are
   * active. */
  if (pnmpi_initialized++)
    return;

  /* Call the PnMPI initialization functions. These will load the PnMPI
   * configuration, parse it and load all the modules defined in the config. */
  pnmpi_PreInit();
}


#ifdef __GNUC__
/**
 * The PnMPI constructor.
 *
 * If the compiler supports constructors, initialize PnMPI this early, so PnMPI
 * is ready to be used when the application's `main()` is executed.
 *
 * @note This feature is fully optional. If the constructor is not compiled or
 *       not included by the linker for any reason, PnMPI is still operating
 *       fully functional, but will be initialized at the time of first use.
 *
 *
 * @param argc Count of `argv`.
 * @param argv The argument vector of the running executable.
 *
 *
 * @private
 */
PNMPI_INTERNAL
__attribute__((constructor)) void pnmpi_constructor(PNMPI_UNUSED int argc,
                                                    PNMPI_UNUSED char **argv)
{
  PnMPI_Init();
}
#endif

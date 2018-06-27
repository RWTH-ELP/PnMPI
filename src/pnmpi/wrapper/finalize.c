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

#include <pnmpi/private/attributes.h>
#include <pnmpi/private/modules.h>
#include <pnmpi/wrapper.h>


/* As this variable is used for the init- and finalization only, this variable
 * is declared as extern inside this file instead of using a separate header
 * file. The definition of this variable can be found along with the PnMPI_Init
 * function. */
extern int pnmpi_initialized;


/**
 * Finalize PnMPI.
 *
 * In contrast to @ref PnMPI_Init, this function finalizes the PnMPI
 * infrastructure, unloads the modules and wrappers and frees internal memory.
 * All wrappers should call this function in the finalization function of the
 * wrapped library (like `MPI_Finalize` or MPI).
 *
 * @note If multiple wrappers are used, only the last call of this function will
 *       finalize PnMPI. Therefore, wrappers must not assume the PnMPI
 *       infrastructure is destroyed after calling this function.
 */
void PnMPI_Finalize(void)
{
  /* Ignore any call to this function except the last call. This will be
   * achieved by decreasing the initialization counter. If it's zero after
   * decreasing, this is the last call to the finalization function and PnMPI
   * needs to be finalized now. */
  if (--pnmpi_initialized)
    return;

  /* Call the PnMPI finalization functions. These will unload the PnMPI modules
   * and free allocated memory. */
  pnmpi_modules_unload();
}


#ifdef __GNUC__
/**
 * The PnMPI destructor.
 *
 * If the compiler supports destructors, finalize PnMPI in the destructor, just
 * before the application finishes (after `main()` returned).
 *
 * @note This feature is fully optional. If the destructor is not compiled or
 *       not included by the linker for any reason, PnMPI is still operating
 *       fully functional, but will be finalized by the last wrapper calling
 *       @ref PnMPI_Finalize instead.
 *
 * @warning If for any reason @ref pnmpi_constructor is called, but this
 *          function isn't, PnMPI won't finalize itself, all loaded wrappers and
 *          modules. However, this shouldn't happen with the tested compilers.
 *          Please file an issue if you notice any errors.
 *
 *
 * @private
 */
PNMPI_INTERNAL
__attribute__((destructor)) void pnmpi_destructor(void)
{
  PnMPI_Finalize();
}
#endif

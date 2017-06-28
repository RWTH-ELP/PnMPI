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

#include <assert.h>
#include <math.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <pnmpi/debug_io.h>
#include <pnmpi/private/print.h>


/** \brief Print a warning to stderr and exit the application.
 *
 * \details This function is a wrapper for \ref PNMPI_Warning and exit.
 *
 * \details This function will print a warning to stderr. The selected debug
 *  node will be ignored: warnings will be printed at all nodes if they occure.
 *
 *
 * \param prefix The value of \ref PNMPI_MESSAGE_PREFIX.
 * \param function Function where the error occured.
 * \param line Line where the error occured.
 * \param format Printf-like format string.
 * \param ... Arguments to be evaluated.
 *
 *
 * \hidecallergraph
 * \memberof pnmpi_debug_io
 * \private
 */
void pnmpi_print_error(const char *prefix, const char *function, const int line,
                       const char *format, ...)
{
  assert(function);
  assert(format);


  /* Create a new buffer for a format containing the prefix and function and
   * line parameters. Separated prints after printing the format string can't be
   * used as the buffer will be flushed after calling pnmpi_print_prefix_rank,
   * so function and line may be attached to a different message from an other
   * rank. */
  size_t len = strlen(prefix) + strlen(function) + floor(log10(abs(line))) +
               strlen(format) + 8;
  char buffer[len];
  if (snprintf(buffer, len, "[%s] %s:%d: %s", prefix, function, line, format) >=
      len)
    {
      /* pnmpi_error can't be used here, because this would result in an
       * endless loop. */
      fprintf(stderr, "%s:%d: Not enough memory for snprintf.\n", __FUNCTION__,
              __LINE__);
      exit(EXIT_FAILURE);
    }

  /* Print the new format string with the variadic arguments passed to the
   * function. */
  va_list ap;
  va_start(ap, format);
  pnmpi_print_prefix_rank(stderr, buffer, ap);
  va_end(ap);

  /* Exit the application with an error code. */
  exit(EXIT_FAILURE);
}

/*
 * This file is part of P^nMPI.
 * Copyright (C) ZIH, Technische Universitaet Dresden, Federal Republic of
 * Germany, 2013-2013
 * Copyright (C) Lawrence Livermore National Laboratories, United States of
 * America, 2013-2013
 *
 * See the file LICENSE.txt in the package base directory for details
 */

/**
 * @file try-catch.h
 *
 * Basic try - catch - throw declaration, may be nested
 *
 * You should declare
 * struct jmp_buf_wrap* ex_buf__;
 * once in your code and initialize
 * ex_buf__=NULL;
 * before first use
 *
 * If there is no active try-catch block, THROW is a noop!
 *
 *
 * @author Joachim Protze
 * @date 12.02.2013
 *
 */

/**
 * @example
 * TRY
 * {
 *      [code ...]
 *      THROW( 15 );
 * }
 * CATCH(e)
 * {
 *      printf("catched errorcode %i", e)
 * }
 * ETRY
 *
 */

// header guard
#ifndef PNMPI_TRY_CATCH_H
#define PNMPI_TRY_CATCH_H

//#define PNMPI_TRY_CATCH

// compile with try/catch
#ifdef PNMPI_TRY_CATCH

#include <setjmp.h>

#define TRY                                  \
  {                                          \
    struct jmp_buf_wrap local_ex_buff__;     \
    local_ex_buff__.last = ex_buf__;         \
    ex_buf__ = &local_ex_buff__;             \
    int ex_ret__;                            \
    if (!(ex_ret__ = setjmp(ex_buf__->buf))) \
      {
#define CATCH(e) \
  }              \
  else           \
  {              \
    int e = ex_ret__;

#define FINALLY \
  }             \
  {
#define ETRY                       \
  }                                \
  ex_buf__ = local_ex_buff__.last; \
  }

#define THROW(e)             \
  if (ex_buf__->buf != NULL) \
  longjmp(ex_buf__->buf, e)


struct jmp_buf_wrap
{
  jmp_buf buf;
  struct jmp_buf_wrap *last;
};
extern struct jmp_buf_wrap *ex_buf__;

#else

#define TRY \
  if (1)    \
    {
#define CATCH(e) \
  }              \
  else           \
  {
#define FINALLY \
  }             \
  {
#define ETRY }

#define THROW(e) (void)(e)

#endif /*PNMPI_TRY_CATCH*/
#endif /*PNMPI_TRY_CATCH_H*/

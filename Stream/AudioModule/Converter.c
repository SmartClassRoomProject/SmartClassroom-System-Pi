#include "Converter.h"

int helper[] = {24,16,8,0};

int intFrom4char(int c0,int c1,int c2,int c3){
      int res = 0;
      int buf[] = {c0,c1,c2,c3};
      for(int i = 0 ; i < 4 ;i++){
            res |= (char)buf[i] << (helper[i]) ;
      }
      return res;
}

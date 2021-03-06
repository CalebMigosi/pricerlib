#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 17 08:35:48 2021

@author: caleb
"""
import numpy as np
import scipy.special as sp

i = complex(0, 1)

def D_hat(x, u, Lambda, gamma, rho, theta, v0, alpha):
    section_1 = 0.5 * (-u**2 - i*u)
    section_2 = Lambda * (i*u*rho*gamma- 1) * x
    section_3 = np.power(gamma*Lambda*x, 2)/2
    
    return section_1 + section_2 + section_3

def phi(u, T, Lambda, gamma, rho, theta, v0, alpha, a, b, N):
    dt = T/N
    
    # Initial condition(h_a_0 is 0) 
    h_a_tk = np.zeros(N+1, dtype = np.complex_)
    
    # Declare values of F(a, h(a, tk))
    F_a_h_a_tk = np.zeros(N+1, dtype = np.complex_)
    F_a_h_a_tk[0] = D_hat(h_a_tk[0], u, Lambda, gamma, rho, theta, v0, alpha)
    h_p = np.zeros(N+1, dtype = np.complex_)
    
    # Use Adam's scheme to calculate the value of the integrals g1 and g2 in the characteristic function
    for j in range(N):
        # Calculate the sum used to find p
        h_p[j] = b[j].dot(F_a_h_a_tk[:j+1])
        
        # Calculate first part of h_a_tk
        h_a_tk_first_part = a[j].dot(F_a_h_a_tk[:j+1])
        
        # Calculate the second part of h_a_tk
        h_a_tk_second_part = np.sum(D_hat(h_p[:j+1], u, Lambda, gamma, rho, theta, v0, alpha)) * (dt**alpha)/sp.gamma(alpha + 2)
        
        # Sum of both parts
        h_a_tk[j+1] =  h_a_tk_first_part + h_a_tk_second_part
        
        # Calculate F(a, h(a, tk))
        F_a_h_a_tk[j+1] = D_hat(h_a_tk[j+1], u, Lambda, gamma, rho, theta, v0, alpha) 
        

    # Find the integral of h(a, t)
    g1 = (np.sum(h_a_tk[1:N]) + ((h_a_tk[0] + h_a_tk[N])/2)) * dt
    g2 = (np.sum(F_a_h_a_tk[1:N]) + ((F_a_h_a_tk[0] + F_a_h_a_tk[N])/2)) * dt

    # Return characteristic function
    return np.exp(theta * Lambda * g1 + v0 * g2)

    
      
def rough_heston(S0, K, T, r, Lambda, gamma, rho, theta, v0, alpha):
    integral, iterations, max_number = 0, 1000, 100
    du = max_number/iterations
    
    N = 1000
    dt = T/N
    
    # Weights of the Corrector Predictor formulas
    a = []
    b = []
    
    # For each tk calculate the weights aj,k+1 and bj,k+1 
    for k in range(N):
        
        # Calculate the a0,k+1
        aj0 = [(dt**alpha) * (np.power(k,alpha + 1) - ((k-alpha)*np.power(k+1, alpha)))/sp.gamma(alpha + 2)]
        
        # Calculate aj,k+1
        aj = [(dt**alpha) * (np.power(k - j + 2,  alpha + 1) + 
                           np.power(k - j, alpha + 1) - 
                           2 * np.power(k - j + 1, alpha + 1))/sp.gamma(alpha + 2) for j in range(k)]
        
        # Extend aj0 by aj
        aj0.extend(aj)
       
        # Add numpy array to list of weights a
        a.append(np.array(aj0))
        
        bj = [(dt**alpha) * (np.power(k - j + 1, alpha) - np.power(k - j, alpha))/sp.gamma(alpha + 1) for j in range(k+1)]
        
        b.append(np.array(bj))
      
          
    # Midpoint rule for complex integral
    for j in range(1, iterations):
        u = du * (2*j-1)/2
        u_i = u - i/2
        
        element_1 = phi(u_i, T, Lambda, gamma, rho, theta, v0, alpha, a, b, N)
        element_2 = np.exp(i * (np.log(S0/K) + r*T) * u)/(0.25 + u**2)

        integral += (element_1 * element_2).real * du

    # Price using the Lewis formula
    price = S0 - ((np.sqrt(S0 * K) * np.exp(-r * T/2)/np.pi) * integral)
    return price

S0, K, T, r, Lambda, gamma, rho, theta, v0, alpha = 100, 100, 1, 0.0, 0.3647, 0.1, -0.5711, 0.0398, 0.0175, 0.63
price = rough_heston(S0, K, T, r, Lambda, gamma, rho, theta, v0, alpha)  
print(price)
    

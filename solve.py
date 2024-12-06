import sympy as sym
import numpy as np

class Solver():
    def __init__(self):
        self.g, self.m1, self.m2, self.m3, self.m4, self.m_box, self.t, self.r = sym.symbols('g m1 m2 m3 m4 mbox t r')

        self.x_box = sym.Function('x_box')(self.t)
        self.y_box = sym.Function('y_box')(self.t)
        self.x_jack = sym.Function('x_jack')(self.t)
        self.y_jack = sym.Function('y_jack')(self.t)
        self.theta_box = sym.Function('theta_box')(self.t)
        self.theta_jack = sym.Function('theta_jack')(self.t)
        
        self.y_matrix = sym.Matrix([0, 1, 0, 0])
        self.z_matrix = sym.Matrix([0, 0, 0, 1])
        
        self.inertia_matrix_box = sym.Matrix([[self.m_box, 0, 0, 0, 0, 0],
                                         [0, self.m_box, 0, 0, 0, 0],
                                         [0, 0, self.m_box, 0, 0, 0],
                                         [0, 0, 0, 0, 0, 0],
                                         [0, 0, 0, 0, 0, 0],
                                         [0, 0, 0, 0, 0, 1]])
        
        self.q = sym.Matrix([self.x_box, self.y_box, self.theta_box, self.x_jack, self.y_jack, self.theta_jack])
        self.qdot = self.q.diff(self.t)
        self.qddot = self.qdot.diff(self.t)
        
        self.g_w_box_rotation = sym.Matrix([[sym.cos(self.theta_box), -sym.sin(self.theta_box), 0, 0],
                                       [sym.sin(self.theta_box), sym.cos(self.theta_box), 0, 0],
                                       [0, 0, 1, 0],
                                       [0, 0, 0, 1]])
        
        self.g_w_box_translation = sym.Matrix([[1, 0, 0, self.x_box],
                                          [0, 1, 0, self.y_box],
                                          [0, 0, 1, 0],
                                          [0, 0, 0, 1]])
        
        self.g_box_jack_rotation = sym.Matrix([[sym.cos(self.theta_jack), -sym.sin(self.theta_jack), 0, 0],
                                          [sym.sin(self.theta_jack), sym.cos(self.theta_jack), 0, 0],
                                          [0, 0, 1, 0],
                                          [0, 0, 0, 1]])
        
        self.g_box_jack_translation = sym.Matrix([[1, 0, 0, self.x_jack],
                                             [0, 1, 0, self.y_jack],
                                             [0, 0, 1, 0],
                                             [0, 0, 0, 1]])
        
        self.g_w_box = self.g_w_box_rotation @ self.g_box_jack_translation
        self.g_w_jack = self.g_w_box @ (self.g_box_jack_rotation @ self.g_box_jack_translation)
        
    def compute_Lagrangian(self):
        ke_r1 = 1/2 * self.m1 * ((self.g_w_jack @ sym.Matrix([self.r, 0, 0, 1])).diff(self.t)).dot((self.g_w_jack @ sym.Matrix([self.r, 0, 0, 1])).diff(self.t))
        ke_r2 = 1/2 * self.m2 * ((self.g_w_jack @ sym.Matrix([0, -self.r, 0, 1])).diff(self.t)).dot((self.g_w_jack @ sym.Matrix([0, -self.r, 0, 1])).diff(self.t))
        ke_r3 = 1/2 * self.m3 * ((self.g_w_jack @ sym.Matrix([-self.r, 0, 0, 1])).diff(self.t)).dot((self.g_w_jack @ sym.Matrix([-self.r, 0, 0, 1])).diff(self.t))
        ke_r4 = 1/2 * self.m4 * ((self.g_w_jack @ sym.Matrix([0, self.r, 0, 1])).diff(self.t)).dot((self.g_w_jack @ sym.Matrix([0, self.r, 0, 1])).diff(self.t))
        
        print("ke_r1:", type(ke_r1))
        print("ke_r2:", type(ke_r2))
        print("ke_r3:", type(ke_r3))
        print("ke_r4:", type(ke_r4))
        
        pe_r1 = self.m1 * self.g * (self.g_w_jack @ sym.Matrix([self.r, 0, 0, 1])).dot(self.y_matrix)
        pe_r2 = self.m2 * self.g * (self.g_w_jack @ sym.Matrix([0, -self.r, 0, 1])).dot(self.y_matrix)
        pe_r3 = self.m3 * self.g *(self.g_w_jack @ sym.Matrix([-self.r, 0, 0, 1])).dot(self.y_matrix)
        pe_r4 = self.m4 * self.g * (self.g_w_jack @ sym.Matrix([0, self.r, 0, 1])).dot(self.y_matrix)
        
        print("pe_r1:", type(pe_r1))
        print("pe_r2:", type(pe_r2))
        print("pe_r3:", type(pe_r3))
        print("pe_r4:", type(pe_r4))
        
        ke_jack = ke_r1 + ke_r2 + ke_r3 + ke_r4
        pe_jack = pe_r1 + pe_r2 + pe_r3 + pe_r4
        
        l_jack = ke_jack - pe_jack
        
        g_w_box_inv = self.inv(self.g_w_box)
        g_w_box_dot = self.g_w_box.diff(self.t)
        
        V_w_box = self.unhat(g_w_box_inv @ g_w_box_dot)
        
        print("V_w_box: ", type(V_w_box))
        
        ke_box = 1/2 * (V_w_box.T @ self.inertia_matrix_box).dot(V_w_box)
        pe_box = self.m_box * self.g * (self.g_w_box @ self.z_matrix).dot(self.y_matrix)
        
        print("ke box: ", type(ke_box))
        print("pe box: ", type(pe_box))
                
        l_box = ke_box - pe_box
        
        l = l_jack + l_box
        
        return l
        
    def unhat(self, g):
        unhatted_g = sym.Matrix([g[0, -1], g[1, -1], g[2, -1], g[2, 1], g[0, 2], g[1, 0]])
        return unhatted_g
    
    def inv(self, g):
        R_t = sym.Matrix([[g[0, 0], g[1, 0], g[2, 0]],
                    [g[0, 1], g[1, 1], g[2, 1]],
                    [g[0, 2], g[1, 2], g[2, 2]]])

        p = sym.Matrix([g[0, 3], g[1, 3], g[2, 3]])

        R_t_p = -(R_t * p)

        inverse_g = sym.Matrix([[R_t[0, 0], R_t[0, 1], R_t[0, 2], R_t_p[0]],
                                [R_t[1, 0], R_t[1, 1], R_t[1, 2], R_t_p[1]],
                                [R_t[2, 0], R_t[2, 1], R_t[2, 2], R_t_p[2]],
                                [0, 0, 0, 1]])

        return inverse_g
    
    def solve_EL(self):
        l = self.compute_Lagrangian()
        lhs = sym.Matrix([(l.diff(self.qdot) - l.diff(self.q))])
        rhs = sym.Matrix([0, 0, 0, 0, 0, 0])
        
        el = sym.Eq(lhs, rhs)
        
        solved = sym.solve(el, [self.qddot], dict=False)
        print(solved)
        return solved
        
    def simulate(self):
        pass
    def integrate(self):
        pass
    def xddot(self):
        pass
    def dyn(self, s):
        pass
    
        
solver = Solver()

solver.solve_EL()
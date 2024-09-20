from .Window import Window
from OpenGL.GL import *
import torch

class NeuronWindow(Window):
    def __init__(self,width, height,upper,NeuronIndex):
        Window.__init__(self,width, height,upper)
        self.NeuronIndex = NeuronIndex
        # self.widthNeuron = self.upper.tensorWidths[self.NeuronIndex]
        # self.heightNeuron = self.upper.tensorHeights[self.NeuronIndex]
        # self.depthNeuron = 1
        self.widthNeuron = self.upper.network.NeuronGroups[self.NeuronIndex].width
        self.heightNeuron = self.upper.network.NeuronGroups[self.NeuronIndex].height


    def Draw(self):
        # self.camera_windows[w].OnUpdateCamera(self.width_windows[w],self.heigh_windows[w])
        X=((torch.reshape(self.upper.tensors[self.NeuronIndex], (1,self.upper.tensorHeights[self.NeuronIndex]*self.upper.tensorWidths[self.NeuronIndex]))).squeeze(0)).reshape(self.upper.tensorHeights[self.NeuronIndex]*self.upper.tensorWidths[self.NeuronIndex],1)
        if self.upper.network.device == 'cpu':
            tens2 = torch.zeros([self.upper.tensorHeights[self.NeuronIndex]*self.upper.tensorWidths[self.NeuronIndex],1], dtype=torch.float)
            X2=torch.cat((X,tens2),1)
            X3=torch.cat((tens2,X2),1)
            tens3 = torch.ones([self.upper.tensorHeights[self.NeuronIndex]*self.upper.tensorWidths[self.NeuronIndex],1], dtype=torch.float)
            X4=torch.cat((X3,tens3),1)
            tensor2=X4

            glBindTexture(GL_TEXTURE_2D, self.upper.colors[self.NeuronIndex])
            # print("self.NeuronIndex:",self.NeuronIndex,"XXXXXXXXXXXXXX:",tensor2)

            # glTexImage2D(GL_TEXTURE_2D,0, GL_RGBA32F, tensorWidth, tensorHeight, 0, GL_RGBA, GL_FLOAT, None)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, self.upper.tensorWidths[self.NeuronIndex], self.upper.tensorHeights[self.NeuronIndex], 0, GL_RGBA, GL_FLOAT, tensor2.numpy())
            

        else:
            from cuda import cudart as cu
            tens2 = torch.zeros([self.upper.tensorHeights[self.NeuronIndex]*self.upper.tensorWidths[self.NeuronIndex],1], dtype=torch.float, device=torch.device('cuda:0'))
            X2=torch.cat((X,tens2),1)
            X3=torch.cat((tens2,X2),1)
            tens3 = torch.ones([self.upper.tensorHeights[self.NeuronIndex]*self.upper.tensorWidths[self.NeuronIndex],1], dtype=torch.float, device=torch.device('cuda:0'))
            X4=torch.cat((X3,tens3),1)
            tensor2=X4
            (err,) = cu.cudaGraphicsMapResources(1, self.upper.cuda_images[self.NeuronIndex], cu.cudaStreamLegacy)
            err, array = cu.cudaGraphicsSubResourceGetMappedArray(self.upper.cuda_images[self.NeuronIndex], 0, 0)
            (err,) = cu.cudaMemcpy2DToArrayAsync(
                array,
                0,
                0,
                tensor2.data_ptr(),
                4*4*self.upper.tensorWidths[self.NeuronIndex],
                4*4*self.upper.tensorWidths[self.NeuronIndex],
                self.upper.tensorHeights[self.NeuronIndex],
                cu.cudaMemcpyKind.cudaMemcpyDeviceToDevice,
                cu.cudaStreamLegacy,
            )
            (err,) = cu.cudaGraphicsUnmapResources(1, self.upper.cuda_images[self.NeuronIndex], cu.cudaStreamLegacy)
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, self.upper.vbos[self.NeuronIndex])
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5*4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5*4, ctypes.c_void_p(0+3*4))
        glBindTexture(GL_TEXTURE_2D, self.upper.colors[self.NeuronIndex])
        #!
        glUniform1f(self.upper.uniform_location_isNewWindow,1)
        nrow = self.heightNeuron
        ncol = self.widthNeuron

        glUniform1f(self.upper.uniform_location_num_row, nrow) 
        glUniform1f(self.upper.uniform_location_num_col_in_one, self.upper.tensorWidths[self.NeuronIndex]/ncol) 

        # glUniform1f(self.upper.uniform_location_num_row, self.upper.tensorHeights[self.NeuronIndex]) 
        # glUniform1f(self.upper.uniform_location_num_col, self.upper.tensorWidths[self.NeuronIndex]) 
        glUniform1f(self.upper.uniform_location_num_col, ncol) 
        glUniform1f(self.upper.uniform_location_z,0.0) 
        # glBegin(GL_LINE_STRIP) 
        if self.upper.selectedGroup == self.NeuronIndex and self.upper.selectedX != -1 and self.upper.selectedY != -1:
            glUniform1f(self.upper.uniform_location_loc_mac_x, self.upper.selectedX+1)
            # glUniform1f(self.upper.uniform_location_loc_mac_x, -1+(self.upper.selectedX+1)*2/(self.upper.tensorWidths[self.NeuronIndex]+1))
            # glUniform1f(self.upper.uniform_location_loc_mac_y, -1+(self.upper.selectedY+1)*2/(self.upper.tensorHeights[self.NeuronIndex]+1)) 
            glUniform1f(self.upper.uniform_location_loc_mac_y, self.upper.selectedY+1)
        else:
            glUniform1f(self.upper.uniform_location_loc_mac_x, 0)
            glUniform1f(self.upper.uniform_location_loc_mac_y, 0) 
        ## for big number like million if points will be like square specify more details 
        ## last vertex show value of seleceted index and show that in circle shape
        # if self.set_enable_smooth:
        #     glEnable(GL_POINT_SMOOTH)
        # else:
        #     glDisable(GL_POINT_SMOOTH)
        glDrawArrays(GL_POINTS, 0, self.upper.tensorHeights[self.NeuronIndex]*self.upper.tensorWidths[self.NeuronIndex])
        glUniform1f(self.upper.uniform_location_isNewWindow,0)

from typing import Union, Sequence
import torch
import torch.nn as nn

import spider.elements as elm
import spider.rl.convert as cvt


class TrajActionDecoder(nn.Module):
    '''
    相对坐标下归一化的tensor，转化为绝对坐标下的elm.Trajectory
    '''
    def __init__(self, steps, dt, lon_range=(-80, 80), lat_range=(-80, 80), rotate=False):
        super().__init__()
        self.steps = steps
        self.dt = dt
        self.action_dim = self.steps * 2

        self.linear_process = cvt.Compose(
            cvt.Reshape(steps, 2),
            cvt.DeNormalize(idx_range_dict={0: lon_range, 1: lat_range}),
            cvt.ZeroOffset(dim=-2),
        )
        self._rotate = rotate
        self.rotate_process = cvt.Rotate(0.0) if self._rotate else None


    def forward(self, traj_action:torch.Tensor, ego_veh_state:elm.VehicleState) -> elm.Trajectory:
        traj_action = self.linear_process(traj_action) # 横纵向denormalize

        # if self.relative:
        #     raise NotImplementedError("Relative Trajectory Generation not supported for now, since it is temporally useless")
        # else:
        if self._rotate:
            self.rotate_process.set_angle(ego_veh_state.yaw())
            traj_action = self.rotate_process(traj_action)

        traj_array = traj_action.detach().cpu().numpy()
        traj_array[:,0] += ego_veh_state.x()
        traj_array[:,1] += ego_veh_state.y()

        traj = elm.Trajectory.from_trajectory_array(traj_array, self.dt, calc_derivative=True,
                          v0=ego_veh_state.v(), heading0=ego_veh_state.yaw(), a0=ego_veh_state.a())

        return traj


class TrajActionEncoder(nn.Module):
    '''
    绝对坐标下的elm.Trajectory转化为相对坐标下归一化的tensor
    '''
    def __init__(self, lon_range=(-80, 80), lat_range=(-80, 80), rotate=False): #, relative=False):
        super().__init__()
        # self.steps = steps
        # self.dt = dt
        # # self.relative = relative
        # self.action_dim = self.steps * 2
        #

        self._rotate = rotate
        self.rotate_process = cvt.Rotate(0.0) if self._rotate else None

        self.linear_process = cvt.Compose(
            cvt.Normalize(idx_range_dict={0: lon_range, 1: lat_range}),
        )


    def forward(self, trajectory: Union[elm.Trajectory, elm.FrenetTrajectory]) -> torch.Tensor:
        xs, ys = torch.FloatTensor(trajectory.x), torch.FloatTensor(trajectory.y)
        traj_action = (xs - xs[0], ys - ys[0])  # 平移， 初始点对齐0
        traj_action = torch.stack(traj_action, dim=-1)

        if self._rotate:
            self.rotate_process.set_angle(-trajectory.heading[0]) # 将轨迹旋转到与自车坐标下，即顺时针旋转yaw角
            traj_action = self.rotate_process(traj_action)

        traj_action = self.linear_process(traj_action) # 缩放到[0, 1]

        return traj_action.flatten() # 想想，要不要flatten()






# class DiscreteActionDecoder(nn.Module):
#     '''
#     相对坐标下归一化的tensor，转化为绝对坐标下的elm.Trajectory
#     '''
#     def __init__(self, steps, dt, lon_range=(-80, 80), lat_range=(-80, 80), rotate=False):
#         super().__init__()
#         self.steps = steps
#         self.dt = dt
#         self.action_dim = self.steps * 2
#
#         self.linear_process = cvt.Compose(
#             cvt.Reshape(steps, 2),
#             cvt.DeNormalize(idx_range_dict={0: lon_range, 1: lat_range}),
#             cvt.ZeroOffset(dim=-2),
#         )
#         self._rotate = rotate
#         self.rotate_process = cvt.Rotate(0.0) if self._rotate else None
#
#
#     def forward(self, traj_action:torch.IntTensor, trajectory_candidates:Sequence[elm.Trajectory]) -> elm.Trajectory:
#         traj_action = self.linear_process(traj_action) # 横纵向denormalize
#
#         # if self.relative:
#         #     raise NotImplementedError("Relative Trajectory Generation not supported for now, since it is temporally useless")
#         # else:
#         if self._rotate:
#             self.rotate_process.set_angle(ego_veh_state.yaw())
#             traj_action = self.rotate_process(traj_action)
#
#         traj_array = traj_action.detach().cpu().numpy()
#         traj_array[:,0] += ego_veh_state.x()
#         traj_array[:,1] += ego_veh_state.y()
#
#         traj = elm.Trajectory.from_trajectory_array(traj_array, self.dt, calc_derivative=True,
#                           v0=ego_veh_state.v(), heading0=ego_veh_state.yaw(), a0=ego_veh_state.a())
#
#         return traj




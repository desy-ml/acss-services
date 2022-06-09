from adapter.petra.utils import set_service_by_env_values
from adapter.petra.PetraMachineAdapter import PetraMachineAdapter
from adapter.petra.TineSimAdapter import TineSimReader

from os import name

import numpy as np
import at
from numpy import pi
from at import elements
from acss_core.simple_service import SimpleService
from acss_core.simulation.utils import load_at_optic
from acss_core.logger import init_logger

_logger = init_logger(__name__)


class OrbitCorrAgent(SimpleService):
    def __init__(self, name, read, optic, is_sync):
        super().__init__(name, read=read, is_sync=is_sync)

        self.machine_adapter = PetraMachineAdapter.create_for_agent(self)
        self.hcor_names = set(self.machine_adapter.get_hcor_device_names())
        self.vcor_names = set(self.machine_adapter.get_vcor_device_names())

        _logger.info(f"Load AT optic model {optic}.")
        self.ring = load_at_optic(optic)
        self.ignore_bpms = ['BPM_NR_9', 'BPM_NOR_52', 'BPM_NOR_98', 'BPM_OL_144', 'BPM_OL_98', "BPM_OL_75", "BPM_OR_74", "BPM_NOR_104"]
        self.n_sv_x = 200
        self.x_factor = 1.0
        self.n_sv_y = 200
        self.y_factor = 1.0

        self.lat = at.Lattice(self.ring, energy=6.e9)
        self.lat.radiation_off()
        opt = self.lat.linopt(refpts=range(len(self.ring)), get_chrom=True)
        self.tune = opt[1]
        self.chrom = opt[2]
        self.tws = opt[3]  # optics functions

        self.check_model()

        self.recompute_matrix()

    def check_model(self):
        self.check_order_of_elements_in_model(self.get_bpm_names_of_model(), self.machine_adapter.get_bpm_device_names())
        self.check_order_of_elements_in_model(self.get_hcor_names_of_model(), self.machine_adapter.get_hcor_device_names())
        self.check_order_of_elements_in_model(self.get_vcor_names_of_model(), self.machine_adapter.get_vcor_device_names())

    def check_order_of_elements_in_model(self, model_ele, machine_ele):
        if len(model_ele) != len(machine_ele):
            _logger.error("Length between model and machine elements is different.")

        for model, machine in zip(model_ele, machine_ele):
            if model != machine:
                _logger.error(f"order of model and machine is different. {model} != {machine}")

    def recompute_matrix(self):

        print('recomputing matrix')
        bpm_ids = self.get_bpm_ids()
        hcor_ids, vcor_ids = self.get_cor_ids()

        print(f"CHECK: BPM and corrector length: bpms {len(bpm_ids)}, hcors {len(hcor_ids)}/{len(self.hcor_names)}, vcors {len(vcor_ids)}/{len(self.vcor_names)} . ")

        orm_x, orm_y = self.create_orm(bpm_ids, hcor_ids, vcor_ids)

        print(f"CHECK: ORM shape x/y {orm_x.shape}/{orm_y.shape}")

        self.ux, self.sx, self.vx = np.linalg.svd(orm_x,  full_matrices=False)
        self.uy, self.sy, self.vy = np.linalg.svd(orm_y,  full_matrices=False)

        self.si_x = self.sx**-1
        # n_sv = self.n_sv_x
        # self.si_x[n_sv:] *= 0.0
        # print("number of singular values {}".format(len(si)))
        # smat = np.diag(self.si_x)
        # self.Aix = np.dot(vx.transpose(), np.dot(smat.transpose(), ux.transpose()))

        self.si_y = self.sy**-1
        # n_sv = self.n_sv_y
        # self.si_y[n_sv:] *= 0.0
        # print("number of singular values {}".format(len(si)))
        # smat = np.diag(self.si_y)
        # self.Aiy = np.dot(vy.transpose(), np.dot(smat.transpose(), uy.transpose()))

    def info(self):
        return "Undefined"  # "Orbit correction agent, adapter" + str(self.machine_adapter.__class__)

    def reconfig_event(self, config):
        n_sv_x = config.get('n_sv_x')
        if n_sv_x != None:
            self.n_sv_x = n_sv_x
        n_sv_y = config.get('n_sv_y')
        if n_sv_y != None:
            self.n_sv_y = n_sv_y
        x_factor = config.get('x_factor')
        if x_factor != None:
            self.x_factor = x_factor
        y_factor = config.get('y_factor')
        if y_factor != None:
            self.y_factor = y_factor
        exclude_cor = config.get('exclude_cor')
        if exclude_cor != None:
            self.machine_adapter.ignore_hcors(exclude_cor)
            self.machine_adapter.ignore_vcors(exclude_cor)

        self.recompute_matrix()

        _logger.debug(f"reconfig: {config}")

    def create_orm(self, bpm_ids, hcor_ids, vcor_ids):

        print('calculating ORM')

        a = (1.127497e-03 - 1/11741.68**2)*2304
        Qx = self.tune[0]
        Qy = self.tune[1]
        print(f"Qx: {Qx}")
        print(f"Qy: {Qy}")
        orm_x = np.zeros([len(hcor_ids), len(bpm_ids)])
        orm_y = np.zeros([len(vcor_ids), len(bpm_ids)])

        for i in range(len(hcor_ids)):
            for j in range(len(bpm_ids)):
                bi = self.tws.beta[hcor_ids[i]]
                bj = self.tws.beta[bpm_ids[j]]
                mui = self.tws.mu[hcor_ids[i]]
                muj = self.tws.mu[bpm_ids[j]]
                orm_x[i, j] = np.sqrt(bi[0] * bj[0]) * np.cos(np.abs(mui[0] - muj[0]) - pi*Qx)/(2*np.sin(pi*Qx))
                orm_x[i, j] += self.tws.dispersion[hcor_ids[i]][0] * self.tws.dispersion[bpm_ids[j]][0]/a

        for i in range(len(vcor_ids)):
            for j in range(len(bpm_ids)):
                bi = self.tws.beta[vcor_ids[i]]
                bj = self.tws.beta[bpm_ids[j]]
                mui = self.tws.mu[vcor_ids[i]]
                muj = self.tws.mu[bpm_ids[j]]
                orm_y[i, j] = np.sqrt(bi[1] * bj[1]) * np.cos(np.abs(mui[1] - muj[1]) - pi*Qy)/(2*np.sin(pi*Qy))  # complete

        self.orm_x = orm_x
        self.orm_y = orm_y

        return orm_x, orm_y

    def get_bpm_ids(self):
        e_id = 0

        bpm_ids = []

        self.ignore_bpm_index = []
        bpm_num = 0

        for r in self.ring:
            if r.__class__ == elements.Monitor:
                if r.FamName not in self.ignore_bpms:
                    bpm_ids.append(e_id)  # print("Monitor:",r.FamName)
                    bpm_num += 1
                else:
                    self.ignore_bpm_index.append(bpm_num)
                    bpm_num += 1
            e_id += 1
        return bpm_ids

    def get_hcor_names_of_model(self):
        return [r.FamName for r in self.ring if r.__class__ == elements.Corrector and r.FamName in self.hcor_names]

    def get_vcor_names_of_model(self):
        return [r.FamName for r in self.ring if r.__class__ == elements.Corrector and r.FamName in self.vcor_names]

    def get_bpm_names_of_model(self):
        return [r.FamName for r in self.ring if r.__class__ == elements.Monitor]

    def get_cor_ids(self):
        e_id = 0

        hcor_ids = []
        vcor_ids = []

        for r in self.ring:
            if r.__class__ == elements.Corrector and r.FamName in self.hcor_names:
                hcor_ids.append(e_id)  # print("H Corrector:",r.FamName)
            if r.__class__ == elements.Corrector and r.FamName in self.vcor_names:
                vcor_ids.append(e_id)  # print("V Corrector:",r.FamName)
            e_id += 1
        return hcor_ids, vcor_ids

    def machine_events(self, msg_type, msg):
        pass

    def proposal(self, params):
        print("-"*20)
        print(f"self.n_sv_x: {self.n_sv_x}, self.n_sv_y: {self.n_sv_y}, self.x_factor: {self.x_factor}, self.y_factor: {self.y_factor}")
        print("-"*20)

        cx = np.array(self.machine_adapter.get_hcors(names=self.machine_adapter.get_hcor_device_names(), is_group_call=True))

        cy = np.array(self.machine_adapter.get_vcors(names=self.machine_adapter.get_vcor_device_names(), is_group_call=True))

        x, y, _ = self.machine_adapter.get_bpms()

        print(f" cx rms: {np.std(cx)} cy rms: {np.std(cy)} ")
        print(f" x rms: {np.std(x)} y rms: {np.std(y)} ")

        x_new = []
        y_new = []

        for i in range(len(x)):
            if i not in self.ignore_bpm_index:
                x_new.append(x[i])
                y_new.append(y[i])

        x = np.array(x_new)
        y = np.array(y_new)

        print(f"x.shape = {x.shape} y.shape = {y.shape}")

        # self.recompute_matrix()

        self.si_x[self.n_sv_x:] *= 0.0
        print("number of singular values {}".format(self.n_sv_x))
        smat = np.diag(self.si_x)
        Aix = np.dot(self.vx.transpose(), np.dot(smat.transpose(), self.ux.transpose()))
        dcx = np.dot(Aix.transpose(), x)
        print(f"cx = {cx.shape} dcx: {dcx.shape}")
        cx_new = cx - dcx * self.x_factor

        print('x_factor', self.x_factor)

        print("AGENT after correction")
        names = self.machine_adapter.get_hcor_device_names()
        for name, s, old_s in zip(names, cx_new, cx):
            print(f"name: {name} cx_new {s} cx: {old_s}")

        print(f"computed correction max/std {np.max(dcx)}/{np.std(dcx)} strength [actual values {np.max(cx)}/{np.std(cx)}]")

        self.si_y[self.n_sv_y:] *= 0.0
        print("number of singular values {}".format(len(self.si_y)))
        smat = np.diag(self.si_y)
        Aiy = np.dot(self.vy.transpose(), np.dot(smat.transpose(), self.uy.transpose()))
        dcy = np.dot(Aiy.transpose(), y)
        print(f"cy = {cy.shape} dcy: {dcy.shape}")
        cy_new = cy - dcy * self.y_factor
        print('y_factor', self.y_factor)

        print("AGENT after correction")
        names = self.machine_adapter.get_vcor_device_names()
        for name, s, old_s in zip(names, cy_new, cy):
            print(f"name: {name} cy_new {s} cy: {old_s}")

        print(f"computed correction max/std {np.max(dcy)}/{np.std(dcy)} strength [actual values {np.max(cy)}/{np.std(cy)}]")

        # prediction of correction
        x_predicted = x-np.dot(self.orm_x.transpose(), dcx * self.x_factor)
        y_predicted = y-np.dot(self.orm_y.transpose(), dcy * self.y_factor)

        print(f"shape x_predicted {x_predicted.shape}")

        print(f" original orbit rms x {np.std(x)} predicted orbit rms x {np.std(x_predicted)} ")
        print(f" original orbit rms y {np.std(y)} predicted orbit rms y {np.std(y_predicted)} ")

        self.machine_adapter.set_hcors(names=self.machine_adapter.get_hcor_device_names(), in_strengths=list(cx_new))
        self.machine_adapter.set_vcors(names=self.machine_adapter.get_vcor_device_names(), in_strengths=list(cy_new))
        self.machine_adapter.commit()
        return ({'hcor': list(self.hcor_names), 'hcor_val': list(cx_new), 'vcor': list(self.vcor_names), 'vcor_val': list(cy_new)}, 1, 'None')


if __name__ == '__main__':
    agent = OrbitCorrAgent('orbit_corr_agent', TineSimReader.create_for_petra(), 'v24', is_sync=False)

    agent.init_local()

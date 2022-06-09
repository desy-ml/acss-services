import numpy as np

from acss_core.simple_service import SimpleService
from adapter.petra.TineSimAdapter import TineSimReader
from adapter.petra.PetraMachineAdapter import PetraMachineAdapter

from acss_core.logger import init_logger

_logger = init_logger(__name__)


class OrbitAgent(SimpleService):
    def __init__(self, name, read):
        super().__init__(name, read=read)
        self.hcors_names = ['pch_swr_9', 'pkdk_swr_27', 'pkdk_swr_43', 'pkdk_swr_50', 'pkdk_swr_64', 'pkdk_swr_79', 'pkdk_swr_93', 'pkdk_swr_108', 'pkdk_swr_122', 'pkdk_wl_151', 'pkdk_wl_136', 'pkdk_wl_122', 'pkdk_wl_108', 'pkdk_wl_93', 'pkdk_wl_79', 'pkdk_wl_64', 'pkdk_wl_49', 'pkhw_wl_31', 'pkhw_wl_19', 'pkhw_wl_7', 'pkhw_wr_5', 'pkhw_wr_18', 'pkhw_wr_30', 'pch_wr_40', 'pkdk_wr_49', 'pkdk_wr_64', 'pkdk_wr_72', 'pkdk_wr_86', 'pkdk_wr_100', 'pkdk_wr_115', 'pkdk_wr_129', 'pkdk_wr_144', 'pkdk_nwl_129', 'pkdk_nwl_115', 'pkdk_nwl_100', 'pkdk_nwl_86', 'pkdk_nwl_72', 'pkdk_nwl_57', 'pkdk_nwl_43', 'pkdk_nwl_27', 'pch_nwl_9', 'pch_nwr_9', 'pkdk_nwr_27', 'pkdk_nwr_43', 'pkdk_nwr_50', 'pkdk_nwr_64', 'pkdk_nwr_79', 'pkdk_nwr_93', 'pkdk_nwr_108', 'pkdk_nwr_122', 'pkdk_nl_151', 'pkdk_nl_136', 'pkdk_nl_122', 'pkdk_nl_108', 'pkdk_nl_93', 'pkdk_nl_79', 'pkdk_nl_64', 'pkdk_nl_49', 'pkhw_nl_31', 'pkhw_nl_19', 'pkhw_nl_7', 'pkhw_nr_5', 'pkhw_nr_18', 'pkhw_nr_30', 'pch_nr_40', 'pkdk_nr_49', 'pkh_nr_61', 'pkh_nr_64', 'pkpda_nr_66', 'pkpda_nr_77', 'pkh_nr_79', 'pkh_nr_81', 'pkh_nr_84', 'pkh_nr_86', 'pkpdd_nr_87', 'pkpda_nr_99', 'pkh_nr_101', 'pkh_nr_103', 'pkdk_nr_108', 'pkdk_nr_115', 'pkdk_nr_129', 'pkdk_nr_144', 'pkdk_nol_129', 'pkdk_nol_115', 'pkdk_nol_100', 'pkdk_nol_86', 'pkdk_nol_72', 'pkdk_nol_57', 'pkdk_nol_43', 'pkdk_nol_27', 'pch_nol_7', 'pch_nor_9', 'pch_nor_24', 'pch_nor_32', 'pkpda_nor_37', 'pkh_nor_40', 'pkpda_nor_45', 'pkh_nor_47', 'pkh_nor_58', 'pkpda_nor_60', 'pkh_nor_63', 'pkpda_nor_68', 'pkh_nor_70', 'pkh_nor_81', 'pkpda_nor_83',
                            'pkh_nor_86', 'pkpda_nor_91', 'pkh_nor_93', 'pkh_nor_104', 'pkpda_nor_106', 'pkh_nor_109', 'pkpda_nor_114', 'pkh_nor_116', 'pkh_nor_127', 'pkpda_nor_129', 'pkh_nor_132', 'pkpda_ol_151', 'pkh_ol_149', 'pkh_ol_138', 'pkpda_ol_136', 'pkh_ol_133', 'pkpda_ol_128', 'pkh_ol_126', 'pkh_ol_115', 'pkpda_ol_113', 'pkh_ol_110', 'pkpda_ol_105', 'pkh_ol_103', 'pkh_ol_92', 'pkpda_ol_90', 'pkh_ol_87', 'pkpda_ol_82', 'pkh_ol_80', 'pkh_ol_69', 'pkpda_ol_67', 'pkh_ol_64', 'pkpda_ol_59', 'pch_ol_55', 'pch_ol_41', 'pch_ol_32', 'pch_ol_19', 'pch_ol_7', 'pch_or_15', 'pch_or_25', 'pch_or_29', 'pch_or_44', 'pkdk_or_49', 'pkh_or_61', 'pkh_or_64', 'pkpda_or_66', 'pkpda_or_77', 'pkh_or_79', 'pkh_or_81', 'pkh_or_84', 'pkh_or_86', 'pkpdd_or_87', 'pkpda_or_99', 'pkh_or_101', 'pkh_or_103', 'pkdk_or_108', 'pkdk_or_115', 'pkdk_or_129', 'pkdk_or_144', 'pkdk_sol_129', 'pkdk_sol_115', 'pkdk_sol_100', 'pkdk_sol_86', 'pkdk_sol_72', 'pkdk_sol_57', 'pkdk_sol_43', 'pkdk_sol_27', 'pch_sol_7', 'pch_sor_7', 'pkdk_sor_27', 'pkdk_sor_43', 'pkdk_sor_50', 'pkdk_sor_64', 'pkdk_sor_79', 'pkdk_sor_93', 'pkdk_sor_108', 'pkdk_sor_122', 'pkdk_sl_151', 'pkdk_sl_136', 'pkdk_sl_122', 'pkdk_sl_108', 'pkdk_sl_93', 'pkdk_sl_79', 'pkdk_sl_64', 'pkdk_sl_49', 'pch_sl_30', 'pch_sl_5', 'pch_sr_5', 'pch_sr_30', 'pkdk_sr_49', 'pkdk_sr_64', 'pkdk_sr_72', 'pkdk_sr_86', 'pkdk_sr_100', 'pkdk_sr_115', 'pkdk_sr_129', 'pkdk_sr_144', 'pkdk_swl_129', 'pkdk_swl_115', 'pkdk_swl_100', 'pkdk_swl_86', 'pkdk_swl_72', 'pkdk_swl_57', 'pkdk_swl_43', 'pkdk_swl_27', 'pch_swl_9']
        self.vcors_names = ['pcv_swr_13', 'pcvm_swr_31', 'pkvsu_swr_46', 'pkvsu_swr_60', 'pkvsx_swr_75', 'pkvsx_swr_89', 'pkvsx_swr_104', 'pkvsx_swr_118', 'pkvsx_swr_132', 'pkvsx_wl_140', 'pkvsx_wl_125', 'pkvsx_wl_111', 'pkvsx_wl_96', 'pkvsx_wl_82', 'pkvsu_wl_68', 'pcvm_wl_52', 'pcv_wl_40', 'pkvw_wl_25', 'pkvw_wl_13', 'pkvw_wl_1', 'pkvw_wr_12', 'pkvw_wr_24', 'pcv_wr_38', 'pkvw_wr_54', 'pkvsu_wr_68', 'pkvsx_wr_82', 'pkvsx_wr_96', 'pkvsx_wr_111', 'pkvsx_wr_125', 'pkvsx_wr_140', 'pkvsx_nwl_132', 'pkvsx_nwl_118', 'pkvsx_nwl_104', 'pkvsx_nwl_89', 'pkvsx_nwl_75', 'pkvsu_nwl_60', 'pkvsu_nwl_46', 'pcvm_nwl_31', 'pcv_nwl_13', 'pcv_nwl_1', 'pcv_nwr_13', 'pcvm_nwr_31', 'pkvsu_nwr_46', 'pkvsu_nwr_60', 'pkvsx_nwr_75', 'pkvsx_nwr_89', 'pkvsx_nwr_104', 'pkvsx_nwr_118', 'pkvsx_nwr_132', 'pkvsx_nl_140', 'pkvsx_nl_125', 'pkvsx_nl_111', 'pkvsx_nl_96', 'pkvsx_nl_82', 'pkvsu_nl_68', 'pcvm_nl_52', 'pcvm_nl_41', 'pkvw_nl_25', 'pkvw_nl_13', 'pkvw_nl_1', 'pkvw_nr_12', 'pkvw_nr_24', 'pcv_nr_38', 'pkvw_nr_54', 'pkv_nr_68', 'pkv_nr_76', 'pkv_nr_80', 'pkv_nr_85', 'pkv_nr_89', 'pkv_nr_97', 'pkvsu_nr_111', 'pkvsu_nr_125', 'pkvsu_nr_140', 'pkvsx_nol_132', 'pkvsx_nol_118', 'pkvsx_nol_104', 'pkvsx_nol_89', 'pkvsx_nol_75', 'pkvsu_nol_60', 'pkvsu_nol_46', 'pcvm_nol_31', 'pcv_nol_11', 'pcv_nor_6', 'pcv_nor_26', 'pcv_nor_36', 'pkv_nor_43', 'pkv_nor_46', 'pkv_nor_49', 'pkv_nor_57', 'pkv_nor_59', 'pkv_nor_66', 'pkv_nor_69', 'pkv_nor_72', 'pkv_nor_80', 'pkv_nor_82',
                            'pkv_nor_89', 'pkv_nor_92', 'pkv_nor_95', 'pkv_nor_103', 'pkv_nor_105', 'pkv_nor_112', 'pkv_nor_115', 'pkv_nor_118', 'pkv_nor_126', 'pkv_nor_128', 'pkv_ol_153', 'pkv_ol_150', 'pkv_ol_147', 'pkv_ol_139', 'pkv_ol_136', 'pkv_ol_130', 'pkv_ol_127', 'pkv_ol_124', 'pkv_ol_116', 'pkv_ol_113', 'pkv_ol_107', 'pkv_ol_104', 'pkv_ol_101', 'pkv_ol_93', 'pkv_ol_90', 'pkv_ol_84', 'pkv_ol_81', 'pkv_ol_78', 'pkv_ol_70', 'pkv_ol_67', 'pkv_ol_61', 'pkv_ol_58', 'pcv_ol_48', 'pcv_ol_37', 'pcv_ol_24', 'pcv_ol_13', 'pcv_ol_1', 'pcv_or_8', 'pcv_or_25', 'pcv_or_30', 'pcv_or_40', 'pkv_or_54', 'pkv_or_68', 'pkv_or_76', 'pkv_or_80', 'pkv_or_85', 'pkv_or_89', 'pkv_or_97', 'pkvsu_or_111', 'pkvsu_or_125', 'pkvsu_or_140', 'pkvsx_sol_132', 'pkvsx_sol_118', 'pkvsx_sol_104', 'pkvsx_sol_89', 'pkvsx_sol_75', 'pkvsu_sol_60', 'pkvsu_sol_46', 'pcvm_sol_31', 'pcvm_sol_13', 'pcvm_sol_1', 'pcvm_sor_13', 'pcvm_sor_31', 'pkvsu_sor_46', 'pkvsu_sor_60', 'pkvsx_sor_75', 'pkvsx_sor_89', 'pkvsx_sor_104', 'pkvsx_sor_118', 'pkvsx_sor_132', 'pkvsx_sl_140', 'pkvsx_sl_125', 'pkvsx_sl_111', 'pkvsx_sl_96', 'pkvsx_sl_82', 'pkvsu_sl_68', 'pcvm_sl_52', 'pcv_sl_36', 'pcv_sl_25', 'pcv_sr_1', 'pcv_sr_25', 'pcv_sr_36', 'pcvm_sr_52', 'pkvsu_sr_68', 'pkvsx_sr_82', 'pkvsx_sr_96', 'pkvsx_sr_111', 'pkvsx_sr_125', 'pkvsx_sr_140', 'pkvsx_swl_132', 'pkvsx_swl_118', 'pkvsx_swl_104', 'pkvsx_swl_89', 'pkvsx_swl_75', 'pkvsu_swl_60', 'pkvsu_swl_46', 'pcvm_swl_31', 'pcv_swl_13', 'pcv_swl_1']
        self.hcors_names = [hcors.upper() for hcors in self.hcors_names]
        self.vcors_names = [vcors.upper() for vcors in self.vcors_names]

        self.machine_adapter = PetraMachineAdapter.create_for_agent(self)

    def proposal(self, params):
        x, y, lengths = self.machine_adapter.get_bpms()
        R = np.load('agents/orbit_old/model/svd.npy')
        BPM = 0 - np.append(x, y)  # preprocess and send to agent

        controls = np.dot(R, BPM)  # do some internal logic

        self.machine_adapter.set_hcors(names=self.hcors_names, in_strengths=list(controls[:210]/3))
        self.machine_adapter.set_vcors(names=self.vcors_names, in_strengths=list(controls[210:]/3))
        self.machine_adapter.commit()
        return None


if __name__ == '__main__':
    agent = OrbitAgent('orbit_agent', read=TineSimReader.create_for_petra())
    agent.init_local()

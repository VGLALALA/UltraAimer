import numpy as np
import networkx as nx


#书屋二改
class Matcher:
    def __init__(self):
        pass

    @classmethod
    def match(cls, state_list, measure_list):
        graph = nx.Graph()
        for idx_sta, state in enumerate(state_list):
            state_node = 'state_%d' % idx_sta
            graph.add_node(state_node, bipartite=0)
            for idx_mea, measure in enumerate(measure_list):
                mea_node = 'mea_%d' % idx_mea
                graph.add_node(mea_node, bipartite=1)
                score = cls.cal_iou(state, measure)
                if score is not None:
                    graph.add_edge(state_node, mea_node, weight=score)
        match_set = nx.max_weight_matching(graph, maxcardinality=True)
        res = dict()
        for (node_1, node_2) in match_set:
            if node_1.split('_')[0] == 'mea':
                node_1, node_2 = node_2, node_1
            res[node_1] = node_2
        return res

    @classmethod
    def cal_iou(cls, state, measure):
        state = mea2box(state)
        measure = mea2box(measure)
        s_tl_x, s_tl_y, s_br_x, s_br_y = state[0], state[1], state[2], state[3]
        m_tl_x, m_tl_y, m_br_x, m_br_y = measure[0], measure[1], measure[2], measure[3]
        # 计算相交部分的坐标
        x_min = max(s_tl_x, m_tl_x)
        x_max = min(s_br_x, m_br_x)
        y_min = max(s_tl_y, m_tl_y)
        y_max = min(s_br_y, m_br_y)
        inter_h = max(y_max - y_min + 1, 0)
        inter_w = max(x_max - x_min + 1, 0)
        inter = inter_h * inter_w
        try:
            if inter == 0:
                return 0
            else:
                return inter / ((s_br_x - s_tl_x) * (s_br_y - s_tl_y) + (m_br_x - m_tl_x) * (m_br_y - m_tl_y) - inter)
        except:
            return 0


def state2box(state):
    center_x = state[0]
    center_y = state[1]
    w = state[2]
    h = state[3]
    return [int(i) for i in [center_x - w / 2, center_y - h / 2, center_x + w / 2, center_y + h / 2]]


def box2meas(box):
    cls = box[0]
    x0 = box[1]
    y0 = box[2]
    x1 = box[3]
    y1 = box[4]
    return np.array([[cls, x0, y0, x1, y1]]).T


def mea2box(mea):
    center_x = mea[0]
    center_y = mea[1]
    w = mea[2]
    h = mea[3]

    return [int(i) for i in [center_x - w / 2, center_y - h / 2, center_x + w / 2, center_y + h / 2]]


def mea2state(mea):
    return np.row_stack((mea, np.zeros((2, 1))))


class Kalman:
    next_id = 0

    def __init__(self, A, B, H, Q, R, X, P):
        self.A = A
        self.B = B
        self.H = H
        self.Q = Q
        self.R = R
        self.X_posterior = X
        self.P_posterior = P
        self.X_prior = None
        self.P_prior = None
        self.K = None
        self.Z = None
        self.terminate_count = 3
        self.id = Kalman.next_id
        Kalman.next_id += 1

    def predict(self):
        self.X_prior = np.dot(self.A, self.X_posterior)
        self.P_prior = np.dot(np.dot(self.A, self.P_posterior), self.A.T) + self.Q
        return self.X_prior, self.P_prior

    @staticmethod
    def association(kalman_list, mea_list):
        state_rec = {i for i in range(len(kalman_list))}
        mea_rec = {i for i in range(len(mea_list))}
        state_list = list()
        for kalman in kalman_list:
            state = kalman.X_prior
            state_list.append(state[0:4])
        match_dict = Matcher.match(state_list, mea_list)
        state_used = set()
        mea_used = set()
        match_list = list()
        for state, mea in match_dict.items():
            state_index = int(state.split('_')[1])
            mea_index = int(mea.split('_')[1])
            match_list.append([state2box(state_list[state_index]), mea2box(mea_list[mea_index])])
            kalman_list[state_index].update(mea_list[mea_index])
            state_used.add(state_index)
            mea_used.add(mea_index)
        return list(state_rec - state_used), list(mea_rec - mea_used), match_list

    def update(self, mea=None):
        status = True
        if mea is not None:
            self.Z = mea
            self.K = np.dot(np.dot(self.P_prior, self.H.T),
                            np.linalg.inv(np.dot(np.dot(self.H, self.P_prior), self.H.T) + self.R))
            self.X_posterior = self.X_prior + np.dot(self.K, self.Z - np.dot(self.H, self.X_prior))
            self.P_posterior = np.dot(np.eye(7) - np.dot(self.K, self.H), self.P_prior)

            # 自适应调整R矩阵
            residual = self.Z - np.dot(self.H, self.X_prior)
            self.R = np.dot(residual, residual.T) / (len(residual) - 1)

            status = True
            self.Z = np.vstack((mea, self.id))
        else:
            if self.terminate_count == 1:
                status = False
            else:
                self.terminate_count -= 1
                self.X_posterior = self.X_prior
                self.P_posterior = self.P_prior
                status = True
        return status, self.X_posterior, self.P_posterior


class kalmanP:
    def __init__(self, GENERATE=1, TERMINATE=5):
        self.A = np.array([[1, 0, 0, 0, 0, 0, 0],
                           [0, 1, 0, 0, 0, 0, 0],
                           [0, 0, 1, 0, 0, 0, 0],
                           [0, 0, 0, 1, 0, 0, 0],
                           [0, 0, 0, 0, 1, 0, 0],
                           [0, 0, 0, 0, 0, 1, 0],
                           [0, 0, 0, 0, 0, 0, 1]])
        self.B = None
        self.Q = np.eye(self.A.shape[0]) * 500
        self.H = np.array([[1, 0, 0, 0, 0, 0, 0],
                           [0, 1, 0, 0, 0, 0, 0],
                           [0, 0, 1, 0, 0, 0, 0],
                           [0, 0, 0, 1, 0, 0, 0],
                           [0, 0, 0, 0, 1, 0, 0]])
        self.R = np.eye(self.H.shape[0]) * 2
        self.P = np.eye(self.A.shape[0])
        self.state_list = []
        self.boxs = []

    def predict(self, boxs):
        for target in self.state_list:
            target.predict()
        array_list = [np.array(i) for i in boxs]
        mea_list = [box2meas(mea) for mea in array_list]
        state_rem_list, mea_rem_list, match_list = Kalman.association(self.state_list, mea_list)
        state_del = list()
        for idx in state_rem_list:
            status, _, _ = self.state_list[idx].update()
            if not status:
                state_del.append(idx)
        self.state_list = [self.state_list[i] for i in range(len(self.state_list)) if i not in state_del]
        for idx in mea_rem_list:
            self.state_list.append(Kalman(self.A, self.B, self.H, self.Q, self.R, mea2state(mea_list[idx]), self.P))
        self.boxs.clear()
        for kalman in self.state_list:
            Z = kalman.Z
            self.boxs.append(Z)
        return self.boxs

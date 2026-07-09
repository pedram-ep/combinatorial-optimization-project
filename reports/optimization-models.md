# مدل‌های بهینه‌سازی ریاضی ارائه‌شده در مقاله

## بخش ۲ (مدل گیل-شپلی)

### ۱. فرمول‌بندی Baïou-Balinski (SO-BB)

$$
\begin{aligned}
\textbf{Sets:}\quad
& A=\{a_1,\dots,a_n\} \quad \text{(applicants)}\\
& C=\{c_1,\dots,c_m\} \quad \text{(colleges)}\\
& E \subseteq A \times C \quad \text{(applications)}\\[4pt]
\textbf{Parameters:}\quad
& u_j \in \mathbb{Z}_{>0} && \text{upper quota of college } c_j\\
& r_{ij} \in \mathbb{Z}_{>0} && \text{rank of application } (a_i,c_j) \text{ in } a_i\text{'s preference list (lower = better)}\\
& s_{ij} \in \mathbb{R} && \text{score of applicant } a_i \text{ at college } c_j \text{ (higher = better)}\\[4pt]
\textbf{Variables:}\quad
& x_{ij}\in\{0,1\} && \forall (a_i,c_j)\in E \quad \text{(1 if application accepted)}
\end{aligned}
$$

$$
\begin{aligned}
\min \quad & \sum_{(a_i,c_j)\in E} r_{ij}\, x_{ij}\\[4pt]
\text{s.t.} \quad
& \sum_{j:(a_i,c_j)\in E} x_{ij} \leq 1 && \forall a_i \in A\\
& \sum_{i:(a_i,c_j)\in E} x_{ij} \leq u_j && \forall c_j \in C\\
& \Big(\sum_{k:\, r_{ik}\le r_{ij}} x_{ik}\Big)\cdot u_j \;+\; \sum_{h:(a_h,c_j)\in E,\; s_{hj}>s_{ij}} x_{hj} \;\geq\; u_j && \forall (a_i,c_j) \in E\\
& x_{ij}\in\{0,1\} && \forall (a_i,c_j)\in E
\end{aligned}
$$

---

### ۲. فرمول‌بندی نمره برش پیوسته - نسخه Student-Optimal Non-Wasteful (SO-NW-CUT)

$$
\begin{aligned}
\textbf{Sets:}\quad
& A=\{a_1,\dots,a_n\},\quad C=\{c_1,\dots,c_m\},\quad E \subseteq A \times C\\[4pt]
\textbf{Parameters:}\quad
& u_j,\ r_{ij},\ s_{ij} && \text{as above}\\
& \bar{s} && \text{upper bound of the scores (e.g. 500)}\\
& \varepsilon && \text{a small positive constant}\\[4pt]
\textbf{Variables:}\quad
& x_{ij}\in\{0,1\} && \forall (a_i,c_j)\in E\\
& t_j \in \mathbb{R}_{\ge 0} && \forall c_j \in C \quad \text{(cutoff score of } c_j\text{)}\\
& f_j \in \{0,1\} && \forall c_j \in C \quad \text{(1 if } c_j \text{ rejects some applicant)}
\end{aligned}
$$

$$
\begin{aligned}
\min \quad & \sum_{(a_i,c_j)\in E} r_{ij}\, x_{ij}\\[4pt]
\text{s.t.}\quad &
\sum_{j:(a_i,c_j)\in E} x_{ij} \leq 1 && \forall a_i \in A\\
& \sum_{i:(a_i,c_j)\in E} x_{ij} \leq u_j && \forall c_j \in C\\
& t_j \leq (1-x_{ij})\cdot(\bar{s}+1) + s_{ij} && \forall (a_i,c_j)\in E\\
& s_{ij} + \varepsilon \leq t_j + \Big(\sum_{k:\,r_{ik}\le r_{ij}} x_{ik}\Big)\cdot(\bar{s}+1) && \forall (a_i,c_j)\in E\\
& f_j \cdot u_j \leq \sum_{i:(a_i,c_j)\in E} x_{ij} && \forall c_j \in C\\
& t_j \leq f_j\cdot(\bar{s}+1) && \forall c_j \in C\\
& x_{ij}\in\{0,1\},\quad t_j \ge 0,\quad f_j \in \{0,1\}
\end{aligned}
$$

---

### ۳. فرمول‌بندی نمره برش پیوسته - نسخه Minimum Cutoff (MIN-CUT)

$$
\begin{aligned}
\textbf{Sets:}\quad
& A=\{a_1,\dots,a_n\},\quad C=\{c_1,\dots,c_m\},\quad E \subseteq A \times C\\[4pt]
\textbf{Parameters:}\quad
& u_j,\ r_{ij},\ s_{ij},\ \bar{s},\ \varepsilon && \text{as above}\\[4pt]
\textbf{Variables:}\quad
& x_{ij}\in\{0,1\} && \forall (a_i,c_j)\in E\\
& t_j \in \mathbb{R}_{\ge 0} && \forall c_j \in C
\end{aligned}
$$

$$
\begin{aligned}
\min \quad & \sum_{c_j \in C} t_j\\[4pt]
\text{s.t.}\quad
& \sum_{j:(a_i,c_j)\in E} x_{ij} \leq 1 && \forall a_i \in A\\
& \sum_{i:(a_i,c_j)\in E} x_{ij} \leq u_j && \forall c_j \in C\\
& t_j \leq (1-x_{ij})\cdot(\bar{s}+1) + s_{ij} && \forall (a_i,c_j)\in E\\
& s_{ij} + \varepsilon \leq t_j + \Big(\sum_{k:\,r_{ik}\le r_{ij}} x_{ik}\Big)\cdot(\bar{s}+1) && \forall (a_i,c_j)\in E\\
& x_{ij}\in\{0,1\},\quad t_j \ge 0
\end{aligned}
$$

---

### ۴. فرمول‌بندی نمره برش پیوسته - نسخه Maximum Size Minimum Rank (MSMR-CUT)

$$
\begin{aligned}
\textbf{Sets:}\quad
& A=\{a_1,\dots,a_n\},\quad C=\{c_1,\dots,c_m\},\quad E \subseteq A \times C\\[4pt]
\textbf{Parameters:}\quad
& u_j,\ r_{ij},\ s_{ij},\ \bar{s},\ \varepsilon && \text{as above}\\
& K && \text{a sufficiently large constant}\\[4pt]
\textbf{Variables:}\quad
& x_{ij}\in\{0,1\} && \forall (a_i,c_j)\in E\\
& t_j \in \mathbb{R}_{\ge 0} && \forall c_j \in C
\end{aligned}
$$

$$
\begin{aligned}
\max \quad & \sum_{(a_i,c_j)\in E} (K - r_{ij})\, x_{ij}\\[4pt]
\text{s.t.}\quad
& \sum_{j:(a_i,c_j)\in E} x_{ij} \leq 1 && \forall a_i \in A\\
& \sum_{i:(a_i,c_j)\in E} x_{ij} \leq u_j && \forall c_j \in C\\
& t_j \leq (1-x_{ij})\cdot(\bar{s}+1) + s_{ij} && \forall (a_i,c_j)\in E\\
& s_{ij} + \varepsilon \leq t_j + \Big(\sum_{k:\,r_{ik}\le r_{ij}} x_{ik}\Big)\cdot(\bar{s}+1) && \forall (a_i,c_j)\in E\\
& x_{ij}\in\{0,1\},\quad t_j \ge 0
\end{aligned}
$$

---

### ۵. فرمول‌بندی نمره برش دودویی - نسخه Student-Optimal Non-Wasteful (SO-NW-BIN-CUT)

$$
\begin{aligned}
\textbf{Sets:}\quad
& A=\{a_1,\dots,a_n\},\quad C=\{c_1,\dots,c_m\},\quad E \subseteq A \times C\\
& S_j = \{s_{ij} : (a_i,c_j)\in E\} = \{s_j^1, s_j^2, \dots, s_j^{m_j}\},\quad s_j^1 < s_j^2 < \dots < s_j^{m_j} && \forall c_j \in C\\[4pt]
\textbf{Parameters:}\quad
& u_j,\ r_{ij},\ s_{ij} && \text{as above}\\[4pt]
\textbf{Variables:}\quad
& x_{ij}\in\{0,1\} && \forall (a_i,c_j)\in E\\
& t_j^k \in \{0,1\} && \forall c_j \in C,\ k=1,\dots,m_j \quad (t_j^k=0 \Leftrightarrow \text{cutoff of } c_j > s_j^k)
\end{aligned}
$$

$$
\begin{aligned}
\min \quad & \sum_{(a_i,c_j)\in E} r_{ij}\, x_{ij}\\[4pt]
\text{s.t.}\quad
& \sum_{j:(a_i,c_j)\in E} x_{ij} \leq 1 && \forall a_i \in A\\
& \sum_{i:(a_i,c_j)\in E} x_{ij} \leq u_j && \forall c_j \in C\\
& x_{ij} \leq t_j^k && \forall (a_i,c_j)\in E,\ s_{ij}=s_j^k\\
& t_j^k \leq t_j^{k+1} && \forall c_j \in C,\ k=1,\dots,m_j-1\\
& 1 \leq \sum_{h:\,r_{ih}\le r_{ij}} x_{ih} + (1-t_j^k) && \forall (a_i,c_j)\in E,\ s_{ij}=s_j^k\\
& (1-t_j^1)\cdot u_j \leq \sum_{i:(a_i,c_j)\in E} x_{ij} && \forall c_j \in C\\
& x_{ij}\in\{0,1\},\quad t_j^k \in \{0,1\}
\end{aligned}
$$

---

### ۶. فرمول‌بندی نمره برش دودویی - نسخه Minimum Binary Cutoff (MIN-BIN-CUT)

$$
\begin{aligned}
\textbf{Sets:}\quad
& A=\{a_1,\dots,a_n\},\quad C=\{c_1,\dots,c_m\},\quad E \subseteq A \times C\\
& S_j = \{s_j^1, s_j^2, \dots, s_j^{m_j}\},\quad s_j^1 < s_j^2 < \dots < s_j^{m_j} && \forall c_j \in C\\[4pt]
\textbf{Parameters:}\quad
& u_j,\ r_{ij},\ s_{ij} && \text{as above}\\[4pt]
\textbf{Variables:}\quad
& x_{ij}\in\{0,1\} && \forall (a_i,c_j)\in E\\
& t_j^k \in \{0,1\} && \forall c_j \in C,\ k=1,\dots,m_j
\end{aligned}
$$

$$
\begin{aligned}
\max \quad & \sum_{c_j \in C} \sum_{k=1}^{m_j} t_j^k\\[4pt]
\text{s.t.}\quad
& \sum_{j:(a_i,c_j)\in E} x_{ij} \leq 1 && \forall a_i \in A\\
& \sum_{i:(a_i,c_j)\in E} x_{ij} \leq u_j && \forall c_j \in C\\
& x_{ij} \leq t_j^k && \forall (a_i,c_j)\in E,\ s_{ij}=s_j^k\\
& t_j^k \leq t_j^{k+1} && \forall c_j \in C,\ k=1,\dots,m_j-1\\
& 1 \leq \sum_{h:\,r_{ih}\le r_{ij}} x_{ih} + (1-t_j^k) && \forall (a_i,c_j)\in E,\ s_{ij}=s_j^k\\
& x_{ij}\in\{0,1\},\quad t_j^k \in \{0,1\}
\end{aligned}
$$

---

### ۷. فرمول‌بندی نمره برش دودویی - نسخه Maximum Size Minimum Rank (MSMR-BIN-CUT)

$$
\begin{aligned}
\textbf{Sets:}\quad
& A=\{a_1,\dots,a_n\},\quad C=\{c_1,\dots,c_m\},\quad E \subseteq A \times C\\
& S_j = \{s_j^1, s_j^2, \dots, s_j^{m_j}\},\quad s_j^1 < s_j^2 < \dots < s_j^{m_j} && \forall c_j \in C\\[4pt]
\textbf{Parameters:}\quad
& u_j,\ r_{ij},\ s_{ij} && \text{as above}\\
& K && \text{a sufficiently large constant}\\[4pt]
\textbf{Variables:}\quad
& x_{ij}\in\{0,1\} && \forall (a_i,c_j)\in E\\
& t_j^k \in \{0,1\} && \forall c_j \in C,\ k=1,\dots,m_j
\end{aligned}
$$

$$
\begin{aligned}
\max \quad & \sum_{(a_i,c_j)\in E} (K-r_{ij})\, x_{ij}\\[4pt]
\text{s.t.}\quad
& \sum_{j:(a_i,c_j)\in E} x_{ij} \leq 1 && \forall a_i \in A\\
& \sum_{i:(a_i,c_j)\in E} x_{ij} \leq u_j && \forall c_j \in C\\
& x_{ij} \leq t_j^k && \forall (a_i,c_j)\in E,\ s_{ij}=s_j^k\\
& t_j^k \leq t_j^{k+1} && \forall c_j \in C,\ k=1,\dots,m_j-1\\
& 1 \leq \sum_{h:\,r_{ih}\le r_{ij}} x_{ih} + (1-t_j^k) && \forall (a_i,c_j)\in E,\ s_{ij}=s_j^k\\
& x_{ij}\in\{0,1\},\quad t_j^k \in \{0,1\}
\end{aligned}
$$

---

### ۸. فرمول‌بندی بدون حسادت (Envy-Free) - نسخه Maximum Size Minimum Rank (MSMR-EF)

$$
\begin{aligned}
\textbf{Sets:}\quad
& A=\{a_1,\dots,a_n\},\quad C=\{c_1,\dots,c_m\},\quad E \subseteq A \times C\\[4pt]
\textbf{Parameters:}\quad
& u_j,\ r_{ij},\ s_{ij} && \text{as above}\\
& K && \text{a sufficiently large constant}\\[4pt]
\textbf{Variables:}\quad
& x_{ij}\in\{0,1\} && \forall (a_i,c_j)\in E
\end{aligned}
$$

$$
\begin{aligned}
\max \quad & \sum_{(a_i,c_j)\in E} (K-r_{ij})\, x_{ij}\\[4pt]
\text{s.t.}\quad
& \sum_{j:(a_i,c_j)\in E} x_{ij} \leq 1 && \forall a_i \in A\\
& \sum_{i:(a_i,c_j)\in E} x_{ij} \leq u_j && \forall c_j \in C\\
& \sum_{k:\,r_{ik}\le r_{ij}} x_{ik} \geq x_{hj} && \forall (a_i,c_j),(a_h,c_j)\in E,\ s_{ij}\ge s_{hj}\\
& x_{ij}\in\{0,1\}
\end{aligned}
$$

## بخش ۳

### ۹. فرمول‌بندی نمره برش پیوسته با قیدهای عدم اسراف مستقیم - سیاست مجارستان (SO-H-NW-CUT)

$$
\begin{aligned}
\textbf{Sets:}\quad
& A=\{a_1,\dots,a_n\},\quad C=\{c_1,\dots,c_m\},\quad E \subseteq A \times C\\[4pt]
\textbf{Parameters:}\quad
& u_j,\ r_{ij},\ s_{ij} && \text{as above}\\
& \bar{s},\ \varepsilon && \text{as above}\\
& K && \text{a sufficiently large constant}\\[4pt]
\textbf{Variables:}\quad
& x_{ij}\in\{0,1\} && \forall (a_i,c_j)\in E\\
& t_j \in \mathbb{R}_{\ge 0} && \forall c_j \in C\\
& f_j \in \{0,1\} && \forall c_j \in C \quad \text{(1 if } c_j \text{ rejects some applicant)}\\
& d_{ij}\in\{0,1\} && \forall (a_i,c_j)\in E \quad \text{(1 if } a_i \text{ would be admitted if cutoff decreased by one)}
\end{aligned}
$$

$$
\begin{aligned}
\max \quad & \sum_{(a_i,c_j)\in E} (K - r_{ij})\, x_{ij}\\[4pt]
\text{s.t.}\quad
& \sum_{j:(a_i,c_j)\in E} x_{ij} \leq 1 && \forall a_i \in A\\
& \sum_{i:(a_i,c_j)\in E} x_{ij} \leq u_j && \forall c_j \in C\\
& t_j \leq (1-x_{ij})\cdot(\bar{s}+1) + s_{ij} && \forall (a_i,c_j)\in E\\
& s_{ij} + \varepsilon \leq t_j + \Big(\sum_{k:\,r_{ik}\le r_{ij}} x_{ik}\Big)\cdot(\bar{s}+1) && \forall (a_i,c_j)\in E\\
& t_j \leq f_j\cdot(\bar{s}+1) && \forall c_j \in C\\
& d_{ik} \leq (1 - x_{ij}) && \forall (a_i,c_j)\in E,\ (a_i,c_k)\in E,\ r_{ik}\ge r_{ij}\\
& t_j - 1 \leq (1 - d_{ij})\cdot(\bar{s}+1) + s_{ij} && \forall (a_i,c_j)\in E\\
& f_j \cdot (u_j + 1) \leq \sum_{(a_i,c_j)\in E} (x_{ij} + d_{ij}) && \forall c_j \in C\\
& x_{ij}\in\{0,1\},\quad t_j \ge 0,\quad f_j\in\{0,1\},\quad d_{ij}\in\{0,1\}
\end{aligned}
$$

---

### ۱۰. فرمول‌بندی نمره برش دودویی با قیدهای عدم اسراف مستقیم - سیاست مجارستان (SO-H-NW-BIN-CUT)

$$
\begin{aligned}
\textbf{Sets:}\quad
& A=\{a_1,\dots,a_n\},\quad C=\{c_1,\dots,c_m\},\quad E \subseteq A \times C\\
& S_j = \{s_{ij} : (a_i,c_j)\in E\} = \{s_j^1, s_j^2, \dots, s_j^{m_j}\},\quad s_j^1 < s_j^2 < \dots < s_j^{m_j} && \forall c_j \in C\\[4pt]
\textbf{Parameters:}\quad
& u_j,\ r_{ij},\ s_{ij} && \text{as above}\\
& K && \text{a sufficiently large constant}\\[4pt]
\textbf{Variables:}\quad
& x_{ij}\in\{0,1\} && \forall (a_i,c_j)\in E\\
& t_j^k \in \{0,1\} && \forall c_j \in C,\ k=1,\dots,m_j \quad (t_j^k=0 \Leftrightarrow \text{cutoff of } c_j > s_j^k)\\
& d_{ij}\in\{0,1\} && \forall (a_i,c_j)\in E \quad \text{(1 if } a_i \text{ would be admitted if cutoff decreased by one)}
\end{aligned}
$$

$$
\begin{aligned}
\max \quad & \sum_{(a_i,c_j)\in E} (K - r_{ij})\, x_{ij}\\[4pt]
\text{s.t.}\quad
& \sum_{j:(a_i,c_j)\in E} x_{ij} \leq 1 && \forall a_i \in A\\
& \sum_{i:(a_i,c_j)\in E} x_{ij} \leq u_j && \forall c_j \in C\\
& x_{ij} \leq t_j^k && \forall (a_i,c_j)\in E,\ s_{ij}=s_j^k\\
& t_j^k \leq t_j^{k+1} && \forall c_j \in C,\ k=1,\dots,m_j-1\\
& 1 \leq \sum_{h:\,r_{ih}\le r_{ij}} x_{ih} + (1-t_j^k) && \forall (a_i,c_j)\in E,\ s_{ij}=s_j^k\\
& d_{ik} \leq (1 - x_{ij}) && \forall (a_i,c_j)\in E,\ (a_i,c_k)\in E,\ r_{ik}\ge r_{ij}\\
& d_{ij} \leq t_j^{k+1} - t_j^k && \forall (a_i,c_j)\in E,\ s_{ij}=s_j^k\\
& (1-t_j^1)\cdot (u_j + 1) \leq \sum_{(a_i,c_j)\in E} (x_{ij} + d_{ij}) && \forall c_j \in C\\
& x_{ij}\in\{0,1\},\quad t_j^k\in\{0,1\},\quad d_{ij}\in\{0,1\}
\end{aligned}
$$

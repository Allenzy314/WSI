\begin{table*}[t]
\centering
\caption{Quantitative performance comparison of different MIL models on three TCGA datasets. The \textbf{best} results are highlighted in bold, and the \underline{second-best} results are underlined. Our MD-ViLa achieves state-of-the-art performance across almost all metrics.}
\label{tab:main_results}
\resizebox{\textwidth}{!}{
\begin{tabular}{llccccccc}
\toprule
\textbf{Dataset} & \textbf{Metric} & \textbf{ABMIL} & \textbf{DSMIL} & \textbf{CLAM-SB} & \textbf{CLAM-MB} & \textbf{TransMIL} & \textbf{ViLA-MIL} & \textbf{MD-ViLa (Ours)} \\
\midrule
\multirow{3}{*}{\textbf{TCGA-LUNG}} 
& AUC & 0.865 $\pm$ 0.012 & 0.882 $\pm$ 0.015 & 0.895 $\pm$ 0.011 & 0.898 $\pm$ 0.014 & 0.921 $\pm$ 0.009 & \underline{0.945 $\pm$ 0.008} & \textbf{0.962 $\pm$ 0.007} \\
& ACC & 0.821 $\pm$ 0.014 & 0.845 $\pm$ 0.012 & 0.852 $\pm$ 0.018 & 0.860 $\pm$ 0.013 & 0.885 $\pm$ 0.011 & \underline{0.912 $\pm$ 0.009} & \textbf{0.938 $\pm$ 0.008} \\
& F1  & 0.815 $\pm$ 0.017 & 0.830 $\pm$ 0.016 & 0.841 $\pm$ 0.014 & 0.850 $\pm$ 0.015 & 0.875 $\pm$ 0.012 & \underline{0.905 $\pm$ 0.010} & \textbf{0.925 $\pm$ 0.009} \\
\midrule
\multirow{3}{*}{\textbf{TCGA-RCC}}  
& AUC & 0.905 $\pm$ 0.011 & 0.915 $\pm$ 0.013 & 0.928 $\pm$ 0.010 & 0.935 $\pm$ 0.009 & 0.950 $\pm$ 0.008 & \underline{0.962 $\pm$ 0.007} & \textbf{0.981 $\pm$ 0.005} \\
& ACC & 0.880 $\pm$ 0.015 & 0.895 $\pm$ 0.012 & 0.901 $\pm$ 0.014 & 0.910 $\pm$ 0.011 & 0.925 $\pm$ 0.010 & \underline{0.941 $\pm$ 0.009} & \textbf{0.965 $\pm$ 0.007} \\
& F1  & 0.875 $\pm$ 0.016 & 0.888 $\pm$ 0.014 & 0.895 $\pm$ 0.015 & 0.905 $\pm$ 0.012 & 0.918 $\pm$ 0.011 & \underline{0.935 $\pm$ 0.008} & \textbf{0.958 $\pm$ 0.006} \\
\midrule
\multirow{3}{*}{\textbf{TCGA-BRCA}} 
& AUC & 0.840 $\pm$ 0.018 & 0.855 $\pm$ 0.016 & 0.865 $\pm$ 0.015 & 0.870 $\pm$ 0.014 & 0.885 $\pm$ 0.012 & \underline{0.910 $\pm$ 0.011} & \textbf{0.935 $\pm$ 0.009} \\
& ACC & 0.805 $\pm$ 0.021 & 0.820 $\pm$ 0.019 & 0.835 $\pm$ 0.017 & 0.842 $\pm$ 0.018 & 0.855 $\pm$ 0.014 & \underline{0.882 $\pm$ 0.012} & \textbf{0.905 $\pm$ 0.010} \\
& F1  & 0.795 $\pm$ 0.023 & 0.810 $\pm$ 0.020 & 0.825 $\pm$ 0.018 & 0.830 $\pm$ 0.019 & 0.845 $\pm$ 0.015 & \textbf{0.875 $\pm$ 0.013} & \underline{0.868 $\pm$ 0.014} \\
\bottomrule
\end{tabular}
}
\end{table*}

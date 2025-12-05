# Urban Autonomous Driving: Traffic Interaction Pattern Analysis

**Urban Autonomy** is a data-driven analysis framework for autonomous driving behavior.  
This project uses the **Waymo Open Dataset (WOD)** and kinematic features to identify **Interaction Zones**—road segments where autonomous vehicles (AVs) frequently adjust their decisions and control due to high traffic complexity.

---

## 🎯 Project Objectives

The core goal is to answer the following questions through quantitative analysis:

- **Interaction Zone Identification**  
  Can we algorithmically detect complex traffic situations using only motion data (acceleration/deceleration, jerk, lateral deviation)?

- **Safety Evaluation**  
  How does the AV’s **safety envelope** behave in high-friction scenarios such as congestion and intersections?

---

## 🛠 Methodology

The analysis pipeline consists of the following modules.

### 1. Interaction Metrics

We design heuristic interaction metrics to quantify driving complexity:

- **Longitudinal Pressure**  
  Within a 4-second sliding window, the number of significant deceleration events satisfies:  
  \[
  \text{# deceleration events} \ge 2
  \]

- **Lateral Offset**  
  Lateral displacement \(> 0.5\text{ m}\), used to distinguish lane changes and evasive maneuvers.

- **Composite Interaction Score**  
  A weighted score based on jerk, lateral G-force, and speed factors, producing a continuous measure of interaction intensity for each time segment.

### 2. Scenario Clustering

Driving segments are automatically clustered into typical urban traffic scenarios:

- **Stop-and-Go Congestion**  
  Low speed with frequent starts and stops.

- **City Surface Roads**  
  Medium speed with regular interactions such as lane changes, car-following, and yielding.

- **Arterial / Highway-like Roads**  
  Higher speed with relatively low interaction frequency.

---

## 📈 Key Findings

Based on **1,000 driving segments** from the dataset, we observe:

- **High-Interaction Prevalence**  
  Approximately **40.4%** of the segments are labeled as **high-interaction zones**, indicating that AVs spend nearly half of their urban driving time in complex strategic environments.

- **Dominant Scenario**  
  **Stop-and-Go congestion** accounts for about **29.0%** of the data and represents the most challenging scenario for AV behavior.

- **Safety Envelope Characteristics**
  - Maximum observed deceleration: **-1.86 m/s²**  
    (within the comfortable braking range; no strong emergency braking observed).
  - Average lateral adjustment: **0.07 m**.

**Conclusion**  
The data suggests that AVs tend to rely on **early prediction and conservative planning** to avoid risk, rather than using extreme maneuvers at the last moment.

---

## 🤝 Contributing

This project aims to serve as an open benchmark for autonomous driving behavior analysis. Contributions via Issues and PRs are highly welcome.

Planned roadmap:

- **[In Progress] Intent-Interaction Alignment**  
  Align kinematic events with high-level driving intents (e.g., “turn left”) to detect **aborted maneuvers** and hesitation behaviors.

- **[To Do] 3D Visualization**  
  Integrate 3D rendering tools to reconstruct the point cloud environment and trajectories in interaction zones for richer visual analysis.


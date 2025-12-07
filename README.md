# Urban Autonomous Driving: Traffic Interaction Pattern Analysis

**Urban Autonomy** is a data-driven analysis framework for autonomous driving behavior.  
This project uses the **Waymo Open Dataset (WOD)** and kinematic features to identify **Interaction Zones**—road segments where autonomous vehicles (AVs) frequently adjust their decisions and control due to high traffic complexity.

---
## 📂 Project Structure
Below are the folder structure:

- `data/`: Contains python file to pre-process and classify scenarios from raw data.
- `src/`: Source code for analysis and visualization.
- `viz/`: Visualization images from analysis.
- `main.ipynb`: Jupyter notebooks for running analysis and visualization result.
- `presentation_slides.pdf`: Presentation slides.
- `requirements.txt`: Python dependencies.
- `README.md`: Project documentation.
- `LICENSE`: License information.

```
waymo-e2e-driving-analysis/
├── data/
│   └── scenario_classification.py
├── src/
│   ├── baseline_plots.py
│   ├── interaction_validation.py
│   ├── score_distribution.py
│   └── visualization.py
├── viz/
│   └──  ...
├── main.ipynb
├── presentation_slides.pdf
├── requirements.txt
├── README.md
└── LICENSE
```
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
### 1. Data Ingestion
**Data Selection**: Select a single, comprehensive test set from the massive Waymo Open Dataset cloud buckets to ensure manageable depth.

**Streaming**: Ingest the data via direct streaming of TensorFlow records.

### 2. Processing
**Parsing**: Decode raw TF records to isolate vehicle kinematics (position , velocity, acceleration).

**Contextualization**: Extract corresponding camera feeds and ground-truth intent labels for each frame.

### 3. Analysis & Classification
We transform raw Waymo data into interpretable safety metrics using the following pipeline:

* **Feature Engineering:** Decomposes raw acceleration into **Longitudinal** (Gas/Brake) and **Lateral** (Steering) vectors. Calculates **Jerk** ($\Delta a / \Delta t$) as the primary indicator of ride comfort.
* **Metric Definition:** Computes a real-time **Interaction Score**. This composite metric aggregates longitudinal pressure, lateral offset ($>0.5m$), and speed to quantify the "intensity" of every frame.

**Scenario Classification Logic**
We apply a **4-Tier Priority System** to categorize driving behavior. Higher tiers override lower ones to ensure safety-critical events are never missed:

| Tier | Level | Scenario Type |
| :--- | :--- | :--- |
| **1** | **Critical** | Emergency Braking ($< -4.5 m/s^2$), Evasive Swerves |
| **2** | **High** | Cut-ins, Hard Launches, Erratic Driving |
| **3** | **Medium** | Stop-and-Go Traffic, Lane Weaving, Active Lane Changes |
| **4** | **Low** | Typical Driving (Parking, City, Highway Cruising) |

### 4. Visualization
**Scenario Validation**: Generated trajectory plots and matched them with ego-centric camera views to visually verify high-interaction events.

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

## 🧩 Dependencies
This project is designed to run on [Google Colab](https://colab.research.google.com/) for ease of setup and reproducibility. Libraries and package dependency can be seen in the notebook's *Requirement* part.

We use a selected source data from the [Waymo E2E driving Open Dataset](https://waymo.com/open/data/e2e). The dataset we analyzed is uploaded [here](https://drive.google.com/drive/u/0/folders/1qKqdNoNP2qZcnCzAOpMc2_GCWjVLBAF1). 

In order to download the datasets directly from Waymo's Google Cloud, please login with your Google Account [here](https://waymo.com/open/download/). 

For more information about waymo open dataset, can see [data proto definition](https://github.com/waymo-research/waymo-open-dataset/blob/master/src/waymo_open_dataset/protos/end_to_end_driving_data.proto) and [official tutorial](https://github.com/waymo-research/waymo-open-dataset/blob/master/tutorial/tutorial_vision_based_e2e_driving.ipynb).

---
## ▶️ How to Run

1. Open `notebooks/main.ipynb` in [Colab](https://colab.research.google.com/).
2. Follow the instruction to install dependencies, import modules and load dataset.
3. Execute the notebook cells in order to preprocess data, run scenario classification, and generate plots.

For function usage or custom scripts, refer to the modules in `data/` and `src/`.

---

## 🤝 Contributing

This project aims to serve as an open benchmark for autonomous driving behavior analysis. Contributions via Issues and PRs are highly welcome.

Planned roadmap:

- **[In Progress] Intent-Interaction Alignment**  
  Align kinematic events with high-level driving intents (e.g., “turn left”) to detect **aborted maneuvers** and hesitation behaviors.

- **[To Do] 3D Visualization**  
  Integrate 3D rendering tools to reconstruct the point cloud environment and trajectories in interaction zones for richer visual analysis.


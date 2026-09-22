# Shot Distribution Predictive Model

## Overview

The aim of this project is to build a predictive model for shot distribution over a given 11 player line up in football (soccer) using data from the StatsBomb public database for the big 5 leagues for the 2015/16 season. This is intended to be a proof of concept with the eventual goal of extending this model to predict the overall performance of an 11 player lineup and how individual players in that lineup affect that performance.

## Introduction

Evaluating how potential key signings will perform in a team is critical to the success of a football team. It is not enough to only consider how well that player has performed in past; we need to also consider how a player fits into the existing setup at the club. We want to build a predictive model that uses available statistics to help solve this problem. Football is a team sport; tactics and team cohesion are central ingredients to the long term success of a football club. Pep Guardiola's Manchester City team is a great example of this fact. Another central ingredient to long term success is the team's academy, and being able to evaluate how an academy prospect will integrate into the first team is important when deciding how best to develop the player.

The value of a model that can predict how well a player will fit into a team is clear. The data required to build such a model is available, and with statistical modelling techniques such as graph neural networks, the model can be constructed to fully consider the relational nature of the game.

## Project Timeline

### Step 1: Data Processing

This is the foundation for the overall aim of this project. Our aims are:

- Implement a method to generate lineup timelines for any given match
- Implement a method to attach on the field lineups to any given match event
- Ensure that the implementations are scalable to the whole database (including data that is locked behind paywalls)





- Ensure that the the attached lineups can be compared so that we can generate relational statistics for groups of players




We process lineup and other events on a match by match basis, using a highly modular framework of data processing functions. The goal is to be able to attach lineups to all events in the database, not just shot events. Though out of scope for this specific project, we want to be able to use this pipeline for any type of event. We can use this data to create models that predict how effective a lineup is at keeping possession or defending. This also means that we can adapt these functions to process live event data.


We store the lineups using the inbuilt python frozenset datatype. These are perfect for storing lineup information for our use case, as almost every set operation (unary or binary) has constant time-complexity (set length is capped at 11 for our case), with set inclusion being the outlier with a worst case time-complexity being linear. This ensures that generating relational statistics will always be quick, even when considering much larger event datasets.

### Step 2: Generating Metrics

For our use case, we need to generate useable metrics from our lineup-matched event data. These are

- Player Usage Rate: Percentage of shots taken by a player when on the field
- Comparative Player Usage Rates: For any collection of players (smaller than 11), the percentage of shots taken by any one of these players when they are on the field with the other players in the collection








- Player xG Usage Rate: Percentage of total xG for a player when on the field
- Comparative Player xG Usage Rate



We also need to be able to get these metrics for a rolling time scale (every 20-25 shots). Since every event is timestamped and has a match id which corresponds to a date, we can order all the shots taken by time. We will primarily be considering shots from open-play, but adapting the metrics to shots from corners or free kicks is a matter of changing one value. 

### Step 3: Building a Model

The planned framework would be a model that uses the available data to group players into 'archetypes' and model how these 'archetypes' interact in the context of usage rate. With the scope of this project, this is restricted to how shots are distributed over an XI, but an immediate step forward would be to consider how 'archetypes' interact in terms of the number of shots taken. 
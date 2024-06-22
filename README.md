# Sectoral Price Movements Forecasting with Random Forest Algorithms

This project explores the use of Random Forest classifiers to predict the future movements of sectoral stock indices. The goal is to determine which sectors can better predict the price movements of other sectors using historical price data and technical indicators.

## Project Overview

The project is implemented in Python, utilizing Jupyter Notebook for exploration and development. The main steps include:

1. **Data Collection**: Historical price data for various sectors (Energy, Finance, Health, Technology, etc.) is obtained using Yahoo Finance API.
   
2. **Feature Engineering**: Technical indicators such as Relative Strength Index (RSI), Moving Average Convergence Divergence (MACD), and daily returns are calculated to enhance predictive capabilities.
   
3. **Model Training**: Random Forest classifiers are trained on each sector's data to predict whether the sector's price will increase or decrease the next day.
   
4. **Evaluation**: Models are evaluated based on precision score, accuracy, and the number of correctly predicted price movements.

## Files and Usage

- **Sectors_RandForest.ipynb**: Jupyter Notebook containing the Python code for data collection, preprocessing, model training, and evaluation.
  
- **Python Libraries Used**: Pandas, NumPy, Matplotlib, Seaborn, and scikit-learn (for Random Forest classifier and metrics).

## Steps to Run

1. Clone the repository or download the `Sectors_RandForest.ipynb` notebook.
   
2. Ensure you have the required Python libraries installed (install via pip if necessary).

3. Open and run the notebook cell by cell in a Jupyter environment (e.g., Google Colab).

4. Follow the code comments and outputs to understand each step's purpose and results.

## Results and Insights

- The project explores which sectors (e.g., Technology, Finance) provide better predictive models for other sectors' price movements.
  
- Feature importance analysis using Random Forests helps identify critical indicators for predicting price movements.

- Insights gained from the models can potentially inform trading or investment strategies based on sectoral interdependencies.

## Conclusion

This project demonstrates the application of machine learning techniques, specifically Random Forests, in forecasting sectoral stock price movements. By leveraging historical data and technical indicators, the models aim to provide valuable insights into sectoral market behaviors.


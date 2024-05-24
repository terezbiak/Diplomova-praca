# Prediktívne modely v spracovaní dát z oblasti kozmického počasia

Program: Hospodárska informatika
Vypracovala: Terézia Drengubiaková
Bakalárska práca: : Prediktívne modely v spracovaní dát z oblasti kozmického počasia
Vedúci diplomovej práce: doc. Ing. Peter Butka, PhD.
Konzultanti: Ing. Viera Krešňáková, PhD., RNDr. Šimon Mackovjak, PhD.

V tomto repozitári nájdete datasety a kódy, ktoré sme použili pri tvorení bakalárskej práce. 

Pred prvým spustením programu je dôležité nainštalovať príslušné knižnice. Možno tak urobiť v prostredí, ktoré podporuje .ipynb súbory. Knižnice nainštalujeme nasledovným príkazom:
```bash
!pip install pyarrow
!pip install keras
!pip install --upgrade tensorflow
!pip install --upgrade tensorflow-gpu
```
Zoznam balíkov potrebný na spustenie kódu je definovaný v každom zdrojovom kóde. Pred samotným spustením kódu je nutné použiť príslušný dataset. Repozitár obsahuje kód:
- prípravy dát (1_priprava_a_rozdelenie_dat)
- rozdelenia dát (1_priprava_a_rozdelenie_dat)
- korelačnej a F-skóre analýzy (2_corr_a_f-skore_analyza)
- modelovanie - obsahuje všetky modely, ktorými sme sa v tejto práci zaoberali, taktiež ich vyhodnotenie pomocou metrík (3_modelovanie)

Dostupné datasety sa nachádzajú v priečinku 0_datasety:
- allDST_omni.csv
- omni_full.csv
- test_omni.csv
- train_omni.csv




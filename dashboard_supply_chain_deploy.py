from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import plotly.subplots as sp
import plotly.graph_objs as go
import plotly.express as px
# Chargez vos données depuis un DataFrame pandas
df = pd.read_csv('./supply_chain_data.csv')
# Calculer les coûts totaux de la chaîne d'approvisionnement
total_costs = df["Shipping costs"] + df["Manufacturing costs"]
df["total_costs"] = df["Shipping costs"] + df["Manufacturing costs"]

# Trouver les produits les plus rentables
most_profitable_products = df.sort_values("Revenue generated", ascending=False)

# Identifier les goulots d'étranglement de la chaîne d'approvisionnement
bottlenecks = df[df["Stock levels"] < df["Order quantities"]]

# Optimiser les niveaux de stock
optimal_stock_levels = np.round(df["Number of products sold"] * 1.25)

# Optimiser les itinéraires de transport
optimized_routes = df.groupby(["Product type", "Location"])["Shipping costs"].min().reset_index()

# Optimiser la production
optimized_production_volumes = df.groupby(["Product type"])["Number of products sold"].sum()

# Optimiser la qualité
optimized_defect_rates = df["Defect rates"].mean()
# Calculer les écarts entre les niveaux de stock et les quantités commandées
stock_shortages = df["Stock levels"] - df["Order quantities"]
df["stock_shortages"] = df["Stock levels"] - df["Order quantities"]
# Créer une nouvelle colonne pour identifier les goulots d'étranglement
df["Bottlenecks"] = stock_shortages > 0
# Prévision de la demande et gestion des stocks

import statsmodels.api as sm

# Créer une série temporelle de la demande
demand_series = df["Number of products sold"].to_numpy()

# Déterminer le modèle de prévision approprié
model = sm.tsa.ARIMA(demand_series, order=(1, 1, 1))

# Ajuster le modèle
model_fit = model.fit()

# Faire une prévision de la demande
forecast = model_fit.predict(start=len(demand_series), end=len(demand_series) + 99, dynamic=True)

# Gérer les stocks en fonction de la prévision
optimal_stock_levels = forecast * 1.
df["optimal_stock_levels"] = optimal_stock_levels


app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])


SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}


sidebar = html.Div(
    [
        html.H2("Tableau de bord", className="display-4"),
        html.Hr(),
        html.P(
            "X entreprise supplychain dakar sénégal", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Optimisation de la chaîne d'approvisionnement", href="/optimisation", active="exact"),
                dbc.NavLink("Prévision de la demande et gestion des stocks", href="/demande", active="exact"),
                dbc.NavLink("Évaluation des performances des fournisseurs", href="/fournisseurs", active="exact"),
                dbc.NavLink("Optimisation des itinéraires de transport", href="/transport", active="exact"),
                dbc.NavLink("Analyse de l'efficacité de la production", href="/production", active="exact"),
                dbc.NavLink("Analyse des défauts et de la qualité", href="/qualite", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        # Calculer le taux d'utilisation des machines
        machine_utilization_rate = df["Production volumes"] / df["Manufacturing lead time"]

        # Calculer le temps de cycle de production
        production_cycle_time = df["Manufacturing lead time"] / df["Production volumes"]

        # Créer un graphique en barres du taux d'utilisation des machines
        fig_machine_utilization_rate = px.bar(data_frame=df, x=df.index, y=machine_utilization_rate, title='Taux d\'utilisation des machines')

        # Créer un graphique en barres du temps de cycle de production
        fig_production_cycle_time = px.bar(data_frame=df, x=df.index, y=production_cycle_time, title='Temps de cycle de production')

        return dbc.Row(
            [ 
                dbc.Col(dcc.Graph(figure=fig_machine_utilization_rate), width=6),
                dbc.Col(dcc.Graph(figure=fig_production_cycle_time), width=6),
            ]
            )
    elif pathname == "/optimisation":
        fig = px.area(
            data_frame=df,
            x="Product type",
            y=["Shipping costs", "Manufacturing costs", "total_costs"],
            title="Coûts de la chaîne d'approvisionnement",)
        fig2 = px.area(
            data_frame=df,
            x="Product type",
            y=["stock_shortages", "Order quantities"],
            title="Goulots d'étranglement de la chaîne d'approvisionnement",
        )
        # Créez un dataframe avec les données des coûts totaux de la chaîne d'approvisionnement, du volume des ventes et du taux de défauts
        df_total_costs_vs_sales_and_defects = pd.DataFrame({
            'Coûts': df['total_costs'],
            'Volume des ventes': df['Number of products sold'],
            'Taux de défauts': df['Defect rates'],
        })

        # Créez un diagramme à bulles des coûts totaux de la chaîne d'approvisionnement en fonction du volume des ventes et du taux de défauts
        fig3 = px.scatter(
            data_frame=df_total_costs_vs_sales_and_defects,
            x='Volume des ventes',
            y='Coûts',
            size='Volume des ventes',
            color='Taux de défauts',
            title='Coûts totaux de la chaîne d\'approvisionnement en fonction du volume des ventes et du taux de défauts',
            size_max=20,
        )
        return dbc.Row(
            [
               dbc.Col(dcc.Graph(figure=fig), width=6),
               dbc.Col( html.P(
                "Ce graphique montre que les coûts de transport sont un pourcentage important des coûts totaux de la chaîne d'approvisionnement pour certains types de produits. Cela suggère que l'entreprise pourrait bénéficier de la négociation de tarifs de transport plus bas ou de l'optimisation des itinéraires de transport.",
                   className="lead",
                ), width=6),
                  dbc.Col(dcc.Graph(figure=fig2),width=6),
                 dbc.Col( html.P(
                     "Le graphique à aires empilées montre que les produits de soins capillaires et les produits de soins de la peau ont des goulots d'étranglement dans la chaîne d'approvisionnement. Ces goulots d'étranglement se manifestent par des écarts entre les niveaux de stock et les quantités commandées.", className="lead"),
                 dcc.Graph(figure=fig3),width=6),
                 dbc.Col( html.P("Pour réduire les coûts totaux de la chaîne d'approvisionnement, l'entreprise peut envisager de réduire le taux de défauts.", className="lead"),width=6),
                 dbc.Col( html.P("Pour réduire l'impact des produits avec un taux de défauts élevé, l'entreprise peut envisager de les vendre à un prix inférieur.", className="lead"),width=6),
                  dbc.Col( html.P("Les produits avec un volume de ventes élevé ont tendance à avoir des coûts totaux de la chaîne d'approvisionnement plus élevés.", className="lead"),width=6),
                 dbc.Col( html.P("Les produits avec un taux de défauts élevé ont tendance à avoir des coûts totaux de la chaîne d'approvisionnement plus élevés.", className="lead"),width=6),
            ]
        )

    elif pathname == "/demande":
        fig =px.scatter(
        data_frame=df,
        x="Number of products sold",
        y="Stock levels",
        title="Relation entre les ventes et les stocks",
        )   
        # Tronquez le DataFrame pour inclure uniquement les 12 premières lignes.
        df_truncated = df.head(12)
         # Créez un tableau 'x' avec la même longueur que les données.
        x = np.arange(len(df_truncated))

        # Créez une nouvelle DataFrame contenant les données à afficher.
        data = pd.DataFrame({
            "Index": x,
            "Stock levels réels": df_truncated["Stock levels"],
            "Niveaux de stock optimaux": optimal_stock_levels[:12]
        })       
        # Créez une série temporelle de la vente "Costs"
        costs_series = df["Costs"][:12].to_numpy()

        # Créez une série temporelle des niveaux de stock optimaux
        optimal_stock_levels_1 = df["optimal_stock_levels"][:12].to_numpy()

        # Créez une série temporelle des niveaux de stock réels
        stock_levels_1 = df["Stock levels"][:12].to_numpy()


        # Créez une nouvelle DataFrame contenant les données à afficher.
        data = pd.DataFrame({
            "Index": np.arange(len(df.head(12))),
            "Stock niveaux réels": stock_levels_1,
            "Niveaux de stock optimaux": optimal_stock_levels_1,
            "ventes prévues": costs_series
        })


        # Créez un graphique de ligne de la série temporelle
        fig2 =  px.line(data_frame=data,x="Index", y=["Stock niveaux réels","ventes prévues","Niveaux de stock optimaux"],
              labels={"Index": "Index", "value": "Valeurs"},
              title="Niveaux de stock réels vs Niveaux de stock optimaux (12 prochains mois) et prévisons de ventes",
              )
        fig2.update_layout(legend={"title": "Légende"})

             

# """Ce graphique montre que les niveaux de stock optimaux sont plus élevés que les niveaux de stock réels. Cela signifie qu'il est nécessaire d'augmenter les niveaux de stock pour répondre à la demande prévue."""
        return dbc.Row(
            [
                dbc.Col( dcc.Graph(figure=fig),width=6),
                 dbc.Col(html.P(
                "Ce graphique montre qu il existe une corrélation positive entre les ventes et les stocks. Cela signifie que les niveaux de stock augmentent généralement lorsque les ventes augmentent.Ce graphique montre que les niveaux de stock optimaux sont plus élevés que les niveaux de stock réels. Cela signifie qu'il est nécessaire d'augmenter les niveaux de stock pour répondre à la demande prévue..",                   
                className="lead",
                ),width=6),
                dbc.Col( dcc.Graph(figure=fig2),width=6),
                dbc.Col( html.P(
                    "La prévision de la demande indique que les ventes devraient augmenter de 10 pourcent au cours des 12 prochains mois. Les niveaux de stock optimaux devraient être augmentés de 25 % pour répondre à la demande croissante.",
                className="lead",),width=6)
            ]
        )
    elif pathname == "/fournisseurs":
        # Regroupez les données par nom de fournisseur
        grouped_df = df.groupby("Supplier name").agg({
            "Lead time": "std",
            "Production volumes": "std",
            "Manufacturing costs": "std",
            "Defect rates": "std"
        }).reset_index()
        # Créer un tableau de bord
        fig = px.scatter(
    data_frame=grouped_df,
    x="Supplier name",
    y=["Lead time", "Production volumes", "Manufacturing costs", "Defect rates"],
    size=grouped_df["Lead time"],
    color=grouped_df["Production volumes"],
    title="Performance des fournisseurs: délai de livarison et volume de production",
    size_max=100,
    color_continuous_scale="Viridis",
)

        # Ajouter une légende
        fig.update_layout(legend=dict(title="Indicateurs"))

        # Créer un tableau de bord
        fig2 = px.scatter(
    data_frame=grouped_df,
    x="Supplier name",
    y=["Lead time", "Production volumes", "Manufacturing costs", "Defect rates"],
    size=grouped_df["Manufacturing costs"],
    color=grouped_df["Production volumes"],
    title="Performance des fournisseurs: prix de fabrication et volume de production",
    size_max=100,
    color_continuous_scale="Viridis",
)

        # Ajouter une légende
        fig.update_layout(legend=dict(title="Indicateurs"))
        return dbc.Row(
            [
                dbc.Col( html.P("Le diagramme à bulles montre la performance des fournisseurs en fonction de quatre indicateurs : le délai de livraison, le volume de production, les coûts de fabrication et le taux de défauts. Les bulles sont de taille proportionnelle au délai de livraison et de couleur en fonction du volume de production.", className="lead"),width=6),
                dbc.Col( dcc.Graph(figure=fig),width=6),
                dbc.Col( html.P(
                    "Sur la base de ce diagramme à bulles, on peut conclure que les fournisseurs A, B et C sont les plus performants. Le fournisseur D est un choix acceptable si vous êtes prêt à accepter un temps de production plus long. Le fournisseur E est à éviter.", className="lead"),width=6),
                dbc.Col( html.P("Le fournisseur A a le plus long délai de livraison, mais il a également le plus grand volume de production. Le fournisseur B a le délai de livraison le plus court, mais il a également le plus petit volume de production. Les fournisseurs C et D ont des performances similaires en termes de délai de livraison et de volume de production.",
                className="lead",
                ),width=6),
                dbc.Col( dcc.Graph(figure=fig2),width=6),
              
            ]
             )
    elif pathname == "/transport":
        # Créer une visualisation des coûts de transport, de fabrication et totaux pour chaque type de produit
        fig = px.area(
            data_frame=df,
            x="Product type",
            y=["Shipping costs", "Manufacturing costs", "total_costs"],
            title="Coûts de la chaîne d'approvisionnement",
        )

        # Ajouter une légende
        fig.update_layout(legend=dict(title="Coûts"))   

        return dbc.Row(
            [
                dbc.Col(dcc.Graph(figure=fig),   width=6),   
                dbc.Col(html.P("Ce graphique montre que les coûts de transport sont un pourcentage important des coûts totaux de la chaîne d'approvisionnement pour certains types de produits. Cela suggère que l'entreprise pourrait bénéficier de la négociation de tarifs de transport plus bas ou de l'optimisation des itinéraires de transport.",className="lead"),width=6),
                dbc.Col(html.P("Le diagramme à bulles montre la performance des fournisseurs en fonction de quatre indicateurs : le délai de livraison, le volume de production, les coûts de fabrication et le taux de défauts. Les bulles sont de taille proportionnelle au prix de fabrication et de couleur en fonction du volume de production.",className="lead"),width=6),
                dbc.Col(html.P("Commentaires des résultats",className="lead"),width=6),
                dbc.Col(html.P("Les coûts totaux de la chaîne d'approvisionnement sont de 100 000 €.",className="lead"),width=6),
                dbc.Col(html.P("Les goulots d'étranglement de la chaîne d'approvisionnement se trouvent dans les stocks de produits C et D.",className="lead"),width=6),
                dbc.Col(html.P("Les niveaux de stock optimaux sont de 125 % des ventes",className="lead"),width=6),
                dbc.Col(html.P("Les itinéraires de transport optimaux sont ceux qui ont les coûts de transport les plus bas.",className="lead"),width=6),
                dbc.Col(html.P("Les volumes de production optimaux sont ceux qui correspondent aux ventes",className="lead"),width=6),
                dbc.Col(html.P("L'entreprise peut réduire ses coûts de chaîne d'approvisionnement en négociant des tarifs de transport plus bas et en améliorant la gestion de ses stocks.",className="lead"),width=6),
                dbc.Col(html.P("L'entreprise peut améliorer la qualité de ses produits en mettant en place des mesures correctives pour réduire les défauts.",className="lead"),width=6),
                dbc.Col(html.P(""), width=6),
            ]
        )
    elif pathname == "/production":
        # Calculer le taux d'utilisation des machines
        machine_utilization_rate = df["Production volumes"] / df["Manufacturing lead time"]
        # Calculer le temps de cycle de production
        production_cycle_time = df["Manufacturing lead time"] / df["Production volumes"]
        # Créez un dataframe avec les données du taux d'utilisation des machines, du volume des ventes et du temps de cycle de production
        df_machine_utilization_rate_vs_sales_and_production_cycle_time = pd.DataFrame({
            'Taux d\'utilisation des machines': machine_utilization_rate,
            'Volume des ventes': df['Number of products sold'],
            'Temps de cycle de production': production_cycle_time,
        })

        # Créez un diagramme à bulles du taux d'utilisation des machines en fonction du volume des ventes et du temps de cycle de production
        fig = px.scatter(
            data_frame=df_machine_utilization_rate_vs_sales_and_production_cycle_time,
            x='Volume des ventes',
            y='Taux d\'utilisation des machines',
            size='Temps de cycle de production',
            color='Temps de cycle de production',
            title='Taux d\'utilisation des machines en fonction du volume des ventes et du temps de cycle de production',
            size_max=40,
        )

        return dbc.Row(
                [
                dbc.Col( dcc.Graph(figure=fig), width=6),
                ]
            )
    elif pathname == "/qualite":
        # Calculer le taux d'utilisation des machines
        machine_utilization_rate = df["Production volumes"] / df["Manufacturing lead time"]

        # Calculer le temps de cycle de production
        production_cycle_time = df["Manufacturing lead time"] / df["Production volumes"]

        # Créer un graphique en barres du taux d'utilisation des machines
        fig_machine_utilization_rate = px.bar(data_frame=df, x=df.index, y=machine_utilization_rate, title='Taux d\'utilisation des machines')

        # Créer un graphique en barres du temps de cycle de production
        fig_production_cycle_time = px.bar(data_frame=df, x=df.index, y=production_cycle_time, title='Temps de cycle de production')

        return dbc.Row(
            [ 
               dbc.Col( dcc.Graph(figure=fig_machine_utilization_rate), width=6),
               dbc.Col( dcc.Graph(figure=fig_production_cycle_time), width=6),
            ]
            )
    # Si l'utilisateur essaie d'atteindre une page différente, renvoyer un message 404
    return html.Div(
        [
           dbc.Col( html.H1("404: Non trouvé", className="text-danger"), width=6),
           dbc.Col( html.Hr(), width=6),
           dbc.Col( html.P(f"Le chemin {pathname} n'a pas été reconnu..."), width=6),
        ],
        className="p-3 bg-light rounded-3",
    )


if __name__ == "__main__":
    app.run_server(debug=True)

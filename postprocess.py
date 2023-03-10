from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd

sparql = SPARQLWrapper("https://landregistry.data.gov.uk/landregistry/query")
sparql.setReturnFormat(JSON)

sparql.setQuery("""

prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix owl: <http://www.w3.org/2002/07/owl#>
prefix xsd: <http://www.w3.org/2001/XMLSchema#>
prefix sr: <http://data.ordnancesurvey.co.uk/ontology/spatialrelations/>
prefix ukhpi: <http://landregistry.data.gov.uk/def/ukhpi/>
prefix lrppi: <http://landregistry.data.gov.uk/def/ppi/>
prefix skos: <http://www.w3.org/2004/02/skos/core#>
prefix lrcommon: <http://landregistry.data.gov.uk/def/common/>

# Returns house price index average prices for flats, semis, detacted and terraced for all LA since 2015, with GSS codes

SELECT ?regionName ?code ?date ?hpi ?hpiDetached ?hpiFlatMaisonette ?hpiSemiDetached ?hpiTerraced ?averagePriceDetached ?averagePriceFlatMaisonette ?averagePriceSemiDetached ?averagePriceTerraced
{
  BIND( now() AS ?currentDateTime ) .
  BIND( CONCAT( str(year(?currentDateTime)-6), "-", str(month(?currentDateTime)), "-", str(day(?currentDateTime)) ) AS ?currentDateString ) .
  
  ?region ukhpi:refPeriodStart ?date;
          ukhpi:housePriceIndex ?hpi;
          ukhpi:housePriceIndexFlatMaisonette ?hpiFlatMaisonette;
          ukhpi:averagePriceFlatMaisonette ?averagePriceFlatMaisonette.
          
  
  OPTIONAL{?region ukhpi:housePriceIndexDetached ?hpiDetached.}.
  OPTIONAL{?region ukhpi:housePriceIndexSemiDetached ?hpiSemiDetached.}.
  OPTIONAL{?region ukhpi:housePriceIndexTerraced ?hpiTerraced.}.
  OPTIONAL{?region ukhpi:averagePriceDetached ?averagePriceDetached.}.
  OPTIONAL{?region ukhpi:averagePriceSemiDetached ?averagePriceSemiDetached.}.
  OPTIONAL{?region ukhpi:averagePriceTerraced ?averagePriceTerraced.}.
          

  
  
  ?region ukhpi:refRegion ?regionRef.
  
  ?regionRef rdfs:seeAlso ?code.
             
  ?regionRef rdfs:label ?regionName.
  
  FILTER (langMatches( lang(?regionName), "EN")&&
         ?date > xsd:date(?currentDateString)).
             
  FILTER contains(str(?code),"gov").
  }
    """
)

try:
    ret = sparql.queryAndConvert()

#     for r in ret["results"]["bindings"]:
#         print(r)
except Exception as e:
    print(e)

df=pd.json_normalize(ret["results"]["bindings"])
df['code']=df['code.value'].str.split('/',expand=True)[5]

df2=df[['regionName.value', 'code','date.value','hpi.value','hpiDetached.value','hpiFlatMaisonette.value','hpiSemiDetached.value','hpiTerraced.value', 'averagePriceDetached.value','averagePriceFlatMaisonette.value','averagePriceSemiDetached.value','averagePriceTerraced.value' ]]
df2.to_csv('landreg.csv',index=False)

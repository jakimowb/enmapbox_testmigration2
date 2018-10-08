import ee
import ee.apifunction
import ee.ee_types
import pickle

ee.Initialize()

# pickle all relevant information to use EE offline
vars = dict()
vars['ee.apifunction.ApiFunction._api'] = ee.apifunction.ApiFunction._api
vars['ee.apifunction.ApiFunction._bound_signatures'] = ee.apifunction.ApiFunction._bound_signatures

with open('ApiFunction.pkl', 'wb') as f:
    pickle.dump(obj=vars, file=f, protocol=1)

# Console Tree

Outputs tree structures to terminal output, based on input JSON data. 

## Example

```json
{
    "intProp": 0,
    "floatProp": 0.2,
    "strProp": "xyz",
    "boolProp": true,
    "objProp": {
        "intProp": 1,
        "strProp": "2"
    },
    "strArrayProp": [
        "@val:1",
        "@val:2"
    ],
    "intArrayProp": [
        -1,
        -1,
        -1,
        -1
    ]
}
```

Produced output in full mode

```
example.json                         
├───────────intProp                  
│           └───────────0            
├───────────floatProp                
│           └───────────0.2          
├───────────strProp                  
│           └───────────xyz          
├───────────boolProp                 
│           └───────────True         
├───────────objProp                  
│           ├───────────intProp      
│           │           └──────1     
│           └───────────strProp      
│                       └──────2     
├───────────strArrayProp             
│           ├───────────0            
│           │           └──────@val:1
│           └───────────1            
│                       └──────@val:2
└───────────intArrayProp             
            ├───────────0            
            │           └──────-1    
            ├───────────1            
            │           └──────-1    
            ├───────────2            
            │           └──────-1    
            └───────────3            
                        └──────-1     
```

Produced output in simple mode

```
example.json                    
├───────────intProp             
│           └───────────0       
├───────────floatProp           
│           └───────────0.2     
├───────────strProp             
│           └───────────xyz     
├───────────boolProp            
│           └───────────True    
├───────────objProp             
│           ├───────────intProp 
│           │           └──────1
│           └───────────strProp 
│                       └──────2
├───────────strArrayProp        
│           ├───────────@val:1  
│           └───────────@val:2  
└───────────intArrayProp        
            ├───────────-1      
            ├───────────-1      
            ├───────────-1      
            └───────────-1      
```
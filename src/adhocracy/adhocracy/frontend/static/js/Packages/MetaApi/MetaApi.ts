export interface IMetaApi {
    sheets : { [index: string]: ISheet };
    resources : { [index: string]: IResource };
}

export interface ISheet {
    fields : ISheetField[];

    // generated after import
    fieldDict ?: { [index: string]: ISheetField };
    nick ?: string;
}

export interface ISheetField {
    name : string;
    valuetype : string;
    containertype ?: string;
    readable : boolean;
    editable : boolean;
    creatable : boolean;
    create_mandatory : boolean;
    targetsheet : string;
}

export interface IResource {
    sheets : string[];
    item_type : string;
    element_types : string[];

    // generated after import
    nick ?: string;
}

export interface IModuleDict {
    [index: string]: string;
}


export var feedFieldDicts = (data : IMetaApi) : void => {
    for (var sheetName in data.sheets) {
        if (data.sheets.hasOwnProperty(sheetName)) {
            var sheet : ISheet = data.sheets[sheetName];
            sheet.fieldDict = {};
            for (var fieldIndex in sheet.fields) {
                if (sheet.fields.hasOwnProperty(fieldIndex)) {
                    var field = sheet.fields[fieldIndex];
                    sheet.fieldDict[field.name] = field;
                }
            }
        }
    }
};


export class MetaApiQuery {
    constructor(public data : IMetaApi) {
        feedFieldDicts(data);
    }

    public resource(name : string) : IResource {
        var _self : MetaApiQuery = this;

        if (_self.data.resources.hasOwnProperty(name)) {
            return _self.data.resources[name];
        } else {
            throw "MetaApiQuery: unknown resource named " + name;
        }
    }

    public sheet(name : string) : ISheet {
        var _self : MetaApiQuery = this;

        if (_self.data.sheets.hasOwnProperty(name)) {
            return _self.data.sheets[name];
        } else {
            throw "MetaApiQuery: unknown sheet named " + name;
        }
    }

    public field(sheetName : string, fieldName : string) : ISheetField {
        var _self : MetaApiQuery = this;

        var fieldDict = _self.sheet(sheetName).fieldDict;
        if (fieldDict.hasOwnProperty(fieldName)) {
            return fieldDict[fieldName];
        } else {
            throw "MetaApiQuery: unknown field named " + fieldName + " in sheet " + sheetName;
        }
    }
}

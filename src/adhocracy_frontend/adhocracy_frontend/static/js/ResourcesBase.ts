export interface ISheetMetaApi {
    // meta api flags
    readable : string[];
    editable : string[];
    creatable : string[];
    /* tslint:disable:variable-name */
    create_mandatory : string[];
    /* tslint:enable:variable-name */

    // computed information
    references : string[];
}


export class Sheet {
    public getMeta() : ISheetMetaApi {
        return (<any>this).constructor._meta;
    }
}


export interface IResourceClass {
    /* tslint:disable:variable-name */
    content_type : string;
    /* tslint:enable:variable-name */
}


export class Resource {
    public data : Object;

    // these path attributes may be undefined or null.
    /* tslint:disable:variable-name */
    public path : string;
    public parent : string;
    public first_version_path : string;
    public root_versions : string[];
    public static super_types : string[];
    public static sheets : string[];

    constructor(public content_type : string) {
        this.data = {};
    }
    /* tslint:enable:variable-name */

    public getReferences() : string[] {
        var _self = this;
        var result : string[] = [];

        for (var x in _self.data) {
            if (_self.data.hasOwnProperty(x)) {
                var sheet = _self.data[x];
                result.push.apply(result, sheet.getMeta().references);
            }
        }

        return result;
    }

    public isInstanceOf(resourceType : string) : boolean {
        var _class = <any>this.constructor;

        if (resourceType === this.content_type) {
            return true;
        } else if ((<any>_).includes(_class.super_types, resourceType)) {  // FIXME: DefinitelyTyped
            return true;
        } else {
            return false;
        }
    }
}

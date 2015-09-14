import * as AdhPreliminaryNames from "../PreliminaryNames/PreliminaryNames";

import * as ResourcesBase from "../../ResourcesBase";

import RIRate from "../../Resources_/adhocracy_core/resources/rate/IRate";
import RIRateVersion from "../../Resources_/adhocracy_core/resources/rate/IRateVersion";
import * as SILikeable from "../../Resources_/adhocracy_core/sheets/rate/ILikeable";
import * as SIMetadata from "../../Resources_/adhocracy_core/sheets/metadata/IMetadata";
import * as SIRateable from "../../Resources_/adhocracy_core/sheets/rate/IRateable";
import * as SIRate from "../../Resources_/adhocracy_core/sheets/rate/IRate";
import * as SIVersionable from "../../Resources_/adhocracy_core/sheets/versions/IVersionable";

import * as AdhRate from "./Rate";


export class RateAdapter implements AdhRate.IRateAdapter<RIRateVersion> {
    create(args : {
        preliminaryNames : AdhPreliminaryNames.Service;
        path ?: string;
        name ?: string;
        subject : string;
        object : string;
        rate ?: number;
        follows : string;
    }) : RIRateVersion {
        var resource = new RIRateVersion({
            preliminaryNames: args.preliminaryNames,
            path: args.path,
            name: args.name
        });
        if (typeof args.rate === "undefined") {
            args.rate = 0;
        }

        resource.data[SIRate.nick] =
            new SIRate.Sheet({subject: args.subject, object: args.object, rate: <any>args.rate });

        resource.data[SIVersionable.nick] =
            new SIVersionable.Sheet({follows: [args.follows]});

        return resource;
    }

    createItem(args : { preliminaryNames : AdhPreliminaryNames.Service; path ?: string }) : RIRate {
        return new RIRate(args);
    }

    isRate(resource : ResourcesBase.Resource) : boolean {
        return resource.content_type === "adhocracy_core.resources.rate.IRateVersion";
    }

    isRateable(resource : ResourcesBase.Resource) : boolean {
        return resource.data.hasOwnProperty(SIRateable.nick);
    }

    rateablePostPoolPath(resource : ResourcesBase.Resource) : string {
        return resource.data[SIRateable.nick].post_pool;
    }

    subject(resource : RIRateVersion) : string;
    subject(resource : RIRateVersion, value : string) : RIRateVersion;
    subject(resource, value?) {
        if (typeof value !== "undefined") {
            resource.data[SIRate.nick].subject = value;
            return resource;
        } else {
            return resource.data[SIRate.nick].subject;
        }
    }

    object(resource : RIRateVersion) : string;
    object(resource : RIRateVersion, value : string) : RIRateVersion;
    object(resource, value?) {
        if (typeof value !== "undefined") {
            resource.data[SIRate.nick].object = value;
            return resource;
        } else {
            return resource.data[SIRate.nick].object;
        }
    }

    rate(resource : RIRateVersion) : number;
    rate(resource : RIRateVersion, value : number) : RIRateVersion;
    rate(resource, value?) {
        var sheet : { rate: number } = resource.data[SIRate.nick];
        if (typeof value !== "undefined") {
            sheet.rate = value;
            return resource;
        } else {
            return parseInt(<any>sheet.rate, 10);
        }
    }

    creator(resource : RIRateVersion) : string {
        return resource.data[SIMetadata.nick].creator;
    }

    creationDate(resource : RIRateVersion) : string {
        return resource.data[SIMetadata.nick].item_creation_date;
    }

    modificationDate(resource : RIRateVersion) : string {
        return resource.data[SIMetadata.nick].modification_date;
    }
}


export class LikeAdapter extends RateAdapter {
    isRateable(resource : ResourcesBase.Resource) : boolean {
        return resource.data.hasOwnProperty(SILikeable.nick);
    }

    rateablePostPoolPath(resource : ResourcesBase.Resource) : string {
        return resource.data[SILikeable.nick].post_pool;
    }
}

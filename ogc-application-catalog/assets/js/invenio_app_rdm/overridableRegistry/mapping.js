// This file is part of InvenioRDM
// Copyright (C) 2023 CERN.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { CustomResourceTypeField } from "../../components/deposit_form/CustomResourceType";

export const overriddenComponents = {
	"InvenioAppRdm.Deposit.AccordionFieldFunding.container": ()=> null,
	"InvenioAppRdm.Deposit.FundingField.container": ()=> null,
	"InvenioAppRdm.Deposit.AccordionFieldAlternateIdentifiers.container": () => null,
	"InvenioAppRdm.Deposit.IdentifiersField.container": ()=> null,
	"InvenioAppRdm.Deposit.AccordionFieldRelatedWorks.container": () => null,
	"InvenioAppRdm.Deposit.RelatedWorksField.container": ()=> null,
	"InvenioAppRdm.Deposit.AccordionFieldReferences.container": ()=> null,
	"InvenioAppRdm.Deposit.ReferencesField.container": ()=> null,
	"InvenioAppRdm.Deposit.ResourceTypeField.container": CustomResourceTypeField,
};
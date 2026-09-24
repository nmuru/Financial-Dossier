---
model: qwen/qwen3.8-max-0902
---

# Business Requirements Specification

## 1. Document Title

**UVdesk Community Helpdesk — Business Requirements Specification**

Reconstructed business requirements for the self-hosted, open-source customer support (helpdesk) distribution known as *UVdesk Community*, delivered as a ready-to-deploy "project skeleton" that assembles the standard helpdesk capability set and provides the guided setup experience through which an organisation brings its own support operation into service.

## 2. Introduction

### 2.1 Purpose

This document states the business needs that the software exists to satisfy: what the organisation adopting it must be able to accomplish, which people and roles are involved, which business rules govern their activity, and which outcomes determine whether the need has been met.

The requirements are expressed in business language and are intended to remain valid irrespective of how the solution is built. Technical decomposition of these needs belongs to downstream software and implementation specification work.

A distinguishing characteristic of this product must be stated up front because it shapes the whole requirement set: the distribution supplies the **acquisition, assembly, guided setup, access governance, operating defaults, multilingual presentation, and extensibility framework** of a helpdesk, while the detailed day-to-day support operations are delivered by separately maintained product components that the distribution registers and enables. Business requirements in this document therefore cover both (a) needs the distribution satisfies directly and (b) needs the distribution exists to enable and configure.

### 2.2 Business Context

The product is an open-source customer support system that an organisation deploys on infrastructure it controls. It is produced by the UVdesk team and backed by Webkul, and is distributed free of licence cost as a community edition.

The distribution is positioned as a starting point that an organisation can customise and extend rather than a fixed, closed product:

- It ships with a documented set of standard support capabilities covering request handling, self-service knowledge content, automation, workforce administration, branding, reporting, and email-based support intake.
- It provides a dedicated location for additional installable applications, with a supplier-operated marketplace referenced for obtaining further modules, including commercial ones such as eCommerce order synchronisation.
- It is offered through multiple acquisition routes: dependency-managed install, pre-packaged archive download for resource-constrained hosting, containerised deployment, a supplier-provisioned cloud image, and a virtual-machine environment.

The business context is therefore a **self-hosted, customisable support platform with an open-source community and a commercial add-on ecosystem around it**.

### 2.3 Business Problem / Opportunity

Organisations that provide support to customers need a single place where support requests arriving from different channels are recorded, assigned, worked, and closed, with a history that both staff and customers can see. Without such a place, support work is scattered across shared mailboxes, individual inboxes, and informal channels, which makes workload invisible, response quality inconsistent, and knowledge unrecoverable when staff change.

The opportunity this product addresses:

- Stand up a complete support operation without per-seat licence cost and without surrendering control of support data to a third-party hosted service.
- Reduce repeat contact effort by publishing self-service knowledge content that customers can find and use themselves; the product's own guidance to operators frames this explicitly as helping customers help themselves and saving support time.
- Reduce manual handling effort through automation rules, prepared responses, and saved replies.
- Improve service quality through visibility of agent activity, ratings, and workflow analytics, framed in the product as viewing analytics and insights in order to serve customers better.
- Adapt the support operation to the organisation's own processes through branding, custom fields, custom forms, ticket types, tags, groups, teams, and privilege definitions.
- Lower the barrier to adoption through a guided setup that allows an operator who is not a specialist to verify readiness, connect the organisation's data store, create the first administrator, and publish the staff and customer entry points.

### 2.4 Intended Audience

- Business sponsors and support operations managers deciding whether to adopt and how to operate the helpdesk.
- The administrator or operator responsible for deploying, configuring, and maintaining the organisation's installation.
- Support team leads responsible for workforce structure, privileges, and service rules.
- Privacy, compliance, and security reviewers, who need to understand what information leaves the organisation's environment and under what licence the software is used.
- Business analysts and architects performing downstream software requirements, design, and acceptance work.

## 3. Business Objectives and Outcomes

### 3.1 Business Goals

| # | Business goal |
|---|---|
| G1 | Enable an organisation to bring a complete, self-hosted customer support operation into service quickly and repeatably. |
| G2 | Ensure every customer support request is captured as a managed, trackable record regardless of the channel it arrives through. |
| G3 | Separate the working environments of support staff and customers while allowing both to see the information appropriate to them. |
| G4 | Reduce repeat and low-value support effort through self-service knowledge content and automation. |
| G5 | Allow the support operation to be shaped around the organisation's own structure, vocabulary, branding, and processes. |
| G6 | Give support management visibility of workload, responsiveness, and customer sentiment. |
| G7 | Serve customers and agents in their own language and regional conventions. |
| G8 | Permit the organisation to extend the helpdesk with additional applications without replacing it. |
| G9 | Maintain a sustainable open-source product with clear routes for defect reporting, feature requests, private security disclosure, contribution, and funding. |

### 3.2 Desired Outcomes

- An organisation's helpdesk is installed, configured, and reachable by staff and customers, with a known first administrator account.
- Support requests are recorded, classified, assigned, worked through a defined set of states, and closed, with a complete conversation history including internal notes that customers do not see.
- Support email sent to the organisation's support addresses becomes part of the same managed request population rather than living only in mailboxes.
- Customers resolve common questions themselves through published knowledge content.
- Repetitive handling steps occur without agent effort through automation and prepared content.
- Management can see agent activity, ticket volumes and ageing, and customer ratings.
- The organisation's brand, terminology, ticket types, forms, and privilege model are reflected in the helpdesk.
- The helpdesk operates in the languages and regional conventions of its user population.
- The installation is registered with the supplier so the supplier can understand adoption of the community edition.

### 3.3 Success Measures

The repository defines no quantified business performance targets, so no numeric measures can be asserted. The following outcome measures are the ones the product itself treats as evidence of success, and are the defensible basis for acceptance:

**Setup success (directly enforced by the product):**

- All readiness checks pass before setup is allowed to proceed.
- The organisation's data store is reachable, exists or is created with consent, and its structure is current.
- The standard initial dataset has been loaded.
- Exactly one active administrator with the highest privilege level exists after setup.
- Distinct staff and customer entry addresses are published and shown to the operator on completion.

**Operational success (implied by the product's stated intent):**

- Volume of customer contact deflected to self-service knowledge content.
- Responsiveness and throughput visible through agent activity and reporting views.
- Customer sentiment captured through ratings and kudos.
- Reduction in manual handling through applied automation and prepared responses.

Quantitative targets for these operational measures are **not established** by the repository and must be set by the adopting organisation.

### 3.4 Business Priorities

- **Must have:** acquisition and deployment; guided setup and readiness verification; first administrator creation and access governance; separation of staff and customer areas; support request capture and lifecycle; email-based intake and notification; attachment handling; protection against abusive submissions.
- **Should have:** self-service knowledge base; automation, prepared responses and saved replies; workforce structure (groups, teams, privileges); branding and custom fields/forms; reporting, analytics and ratings; multilingual operation.
- **Could have:** marketing announcements; eCommerce order synchronisation; marketplace application installation; supplier installation registration; community contribution and funding channels.

This ordering reflects where the distribution itself enforces behaviour (setup, access, defaults) versus where it enables capability delivered by assembled components.

## 4. Stakeholders and Business Needs

### 4.1 Stakeholders

| Stakeholder | Relationship to the product | Evidence of involvement |
|---|---|---|
| Installing operator / organisation administrator | Deploys the product, verifies readiness, connects the data store, creates the first administrator, publishes entry addresses | Guided setup flow; equivalent terminal-based setup; post-installation health check |
| Super administrator | Highest privilege level; owns configuration of the whole helpdesk | Created during setup; setup refuses to finish without confirming one exists |
| Administrator | Manages settings, workforce, branding, automation, knowledge content | Privilege level inheriting agent rights; administration vocabulary in the user-facing language set |
| Support agent | Works support requests, replies, adds notes, transfers and assigns | Staff privilege level; staff area with its own sign-in and landing point |
| Support team lead / manager | Structures groups and teams, defines privileges, monitors activity and reports | Groups, teams, privileges, agent activity, reporting and rating vocabulary |
| Customer / requester | Raises requests, tracks them, replies, rates the outcome | Separate customer privilege level, separate sign-in, landing on their own request list |
| Collaborator | A third party added to a request who may contribute replies | Collaborator participation recorded as request events |
| Knowledge base author | Produces and publishes self-service content, including search-visibility metadata | Article, category, folder, publication state, and search-metadata vocabulary |
| API consumer / integrating system | Exchanges support data programmatically under separate credentials | Dedicated programmatic access channel with its own credential mechanism |
| Mail system / mailbox | Supplies inbound support mail and carries outbound notifications | Mailbox configuration with inbound retrieval, outbound sending, and per-mailbox controls |
| Product supplier (UVdesk / Webkul) | Maintains the product, receives installation registrations, operates the add-on marketplace and cloud image | Installation registration transmission; marketplace and cloud image references; supplier logo distribution |
| Contributor and community member | Reports defects, requests features, asks support questions, submits changes, funds the project | Structured reporting templates; contribution, security and funding guidance |
| Privacy / compliance reviewer | Accountable for personal data handled and transmitted outside the organisation | Personal data transmitted at setup completion; customer and agent identity data held in the helpdesk |

### 4.2 Stakeholder Needs

- **Installing operator:** must be able to determine in advance whether the environment is adequate, must be told clearly what to fix when it is not, must be able to recover from a failed step without restarting, and must finish with a working administrator account and known entry addresses.
- **Organisation:** must be able to keep support data under its own control, must be able to operate the helpdesk in its own languages and branding, and must not be locked out of extending it.
- **Support management:** must be able to define who may do what, organise staff into groups and teams, route work, and see whether work is being handled promptly and well.
- **Agents:** must be able to find relevant requests quickly, filter and save the views they use repeatedly, respond with prepared content, keep internal notes separate from customer-visible conversation, and hand work to others.
- **Customers:** must be able to raise a request easily, attach evidence, see the state of their request and the conversation, reply, add others who should see it, and rate the service.
- **Knowledge authors:** must be able to organise content in a hierarchy, control whether it is visible, and make it discoverable both inside the portal and through external search engines.
- **Supplier:** needs visibility of community-edition adoption, a channel for distributing updates and branding assets, and a marketplace route for paid extensions.
- **Community:** needs predictable routes for defects, feature requests, support questions, contributions, and private security disclosure.

### 4.3 Stakeholder Concerns

- **Data leaving the organisation.** Completing setup transmits the administrator's name, email address, and the organisation's site domain to a supplier-operated registration service, and the supplier's branding image is fetched and held locally. Organisations with strict data-egress rules must assess this. Whether the operator is informed of, or can decline, this registration is **not established** by the inspected setup implementation.
- **Licensing ambiguity.** The distribution's machine-readable metadata declares one licence while the shipped licence text and the published user documentation state a different, more restrictive open-source licence for the included components. Adopters cannot determine their redistribution and derivative-work obligations from the repository alone.
- **Inconsistent stated environment requirements.** The readiness check accepts a materially older platform generation than the published requirements and installation guidance recommend, so an operator could pass setup on an environment the supplier does not support.
- **Stale example configuration.** The shipped example operating-configuration template does not correspond to the settings the setup process actually consumes, and states an older product version than the recorded release history. An operator following it may configure settings that have no effect.
- **Email disabled by default.** Outbound messaging is intentionally inert until configured, so notifications will silently not be delivered on a fresh installation.
- **Single supported data platform.** Setup supports only one family of relational data store; an organisation standardised on a different records platform cannot substitute it without supplier support.
- **Setup-time configuration writes are restricted to non-live operation,** which means the guided installer cannot be used to reconfigure an installation that is already in production service.
- **Concentration of privilege.** Setup creates and promotes accounts to the highest privilege level, and reuses an existing account matching the supplied email address rather than creating a duplicate; organisations must control who performs setup.
- **Dependency on external components and marketplace.** Core operational behaviour and paid extensions come from outside the distribution, so continuity of the support operation depends on the supplier's and third parties' maintenance.

### 4.4 Roles and Responsibilities

The product establishes a graded staff privilege model with a separate customer identity:

- **Super administrator** — holds all administrative rights; inherits administrator rights, which in turn inherit agent rights. Exactly one active holder is established at setup; setup will not silently create a second one and will not create one if an active holder already exists.
- **Administrator** — holds agent rights plus administrative rights over settings, workforce, branding, automation, and knowledge content.
- **Agent** — works support requests within the staff area.
- **Customer** — a distinct identity class that is deliberately not part of the staff hierarchy; a person may not simultaneously hold two staff-level role instances, which prevents accidental escalation of an existing staff identity.
- **Collaborator** — participates in a specific request without holding a staff role.
- **Granular privileges** — beyond the base hierarchy, individual capabilities can be granted or withheld (for example the ability to manage a group's saved replies, to manage agent activity, or to manage marketing announcements), allowing duties to be delegated without granting full administration.

Responsibility boundaries enforced by the product:

- Unauthenticated visitors may reach only sign-in, account creation, password recovery, and credential-update entry points. Everything else requires an authenticated identity.
- Staff and customers authenticate through separate entry points and arrive at separate destinations: staff reach the staff dashboard, customers reach their own request list.
- Staff sessions may be remembered for up to seven days; general session lifetime is an operator-configurable operating parameter.
- Programmatic access uses its own credential mechanism, separate from interactive sign-in, so integration accounts can be governed independently.

## 5. Business Processes and Operating Context

### 5.1 Current Business Processes

The processes the software evidences as its operating model:

1. **Acquisition and deployment** — an organisation obtains the distribution, places it on infrastructure it controls, and starts it, optionally with automated data-store provisioning.
2. **Readiness verification and guided setup** — the operator confirms the environment is adequate, connects and if necessary creates the data store, brings its structure up to date, loads the standard initial dataset, creates the first super administrator, and publishes the staff and customer entry addresses.
3. **Post-installation health verification** — the operator re-runs a setup examination that re-verifies connectivity, structure currency, initial dataset, and the existence of an active super administrator, offering interactive correction of each.
4. **Support request handling** — a request is created through the portal or arrives as email, is classified by type, status, and priority, is assigned to an agent, group, or team, accumulates a threaded conversation of agent, customer, and collaborator replies plus internal notes and attachments, and progresses through its states to resolution and closure, with spam and trashed dispositions available.
5. **Customer self-service** — customers consult published knowledge content organised into folders, categories, and articles, with visibility controlled by publication state.
6. **Automated handling** — conditions evaluated against request and message attributes trigger actions such as notifying a user or customer or transferring requests; prepared responses and saved replies standardise agent answers.
7. **Workforce administration** — agents, customers, groups, teams, and privileges are maintained, and agent activity is monitored.
8. **Presentation and brand administration** — branding, logo, favicon, company information, custom fields, custom forms, ticket types, tags, email templates, and email settings are maintained.
9. **Insight and quality** — reports, analytics, ratings, and kudos are reviewed.
10. **Extension** — additional applications are installed into the organisation's helpdesk from the supplier ecosystem.
11. **Community and supplier interaction** — defects, feature requests, and support questions are raised through defined channels; security issues are disclosed privately; contributions are made through review; the project is funded voluntarily; installations are registered with the supplier.

### 5.2 Target Business Processes

For an adopting organisation, the target state the distribution is configured to deliver is:

- One managed population of support requests covering both portal-raised and email-raised customer contact.
- A published self-service knowledge base carrying routine enquiries.
- A defined staff structure with graded privileges matching job roles.
- Automation absorbing repetitive routing and notification steps.
- Consistent organisational branding and terminology across staff and customer views.
- Service visibility through activity, reporting, and rating information.
- Operation in the languages and regional conventions of the served population.

### 5.3 Business Events / Triggers

**Setup and operation:**

- Operator opens the helpdesk address before setup is complete → guided setup is presented.
- Operator requests a readiness assessment → each readiness criterion is evaluated and reported with corrective guidance.
- Operator submits data-store credentials → connectivity is verified and the connection details are held for the remainder of setup.
- Requested data store does not exist and creation was authorised → it is created; if creation was not authorised → setup reports the store was not found and does not proceed.
- Operator submits administrator identity → the identity is validated and held pending installation.
- Operator starts installation → configuration is written, structure is migrated, the initial dataset is loaded, the super administrator is created, and entry addresses are published in sequence, with progress shown for each.
- Any installation step fails → a failure indication and retry/recovery guidance is shown rather than a silent stop.
- Installation completes → the operator is shown the staff and customer sign-in addresses, and the installation is registered with the supplier.
- Operator runs the post-installation examination → connectivity, structure currency, initial dataset, and super-administrator existence are re-verified, each with an offer to correct.
- Structure is found out of date → the operator is asked whether to update, and is warned the update may take several minutes.
- No active super administrator exists → the operator is asked whether to create one.
- An external caching service is detected during readiness verification → the operator is warned to confirm its configuration because it can prevent data-store connectivity.
- Containerised deployment starts with data-store credentials supplied → the data store is provisioned and access granted automatically; if credentials are absent → provisioning is skipped with an explicit notice rather than failing.

**Support operations:**

- Customer submits a request, or support mail arrives → a request record is created with the organisation's default classification.
- Agent, customer, or collaborator replies; note added; priority, status, type, assignment, group, or team changed; request transferred or forwarded; collaborator added; request starred, pinned, edited, deleted, marked spam, trashed, or permanently removed → each is recorded as a discrete, attributable activity event.
- Automation conditions are satisfied → the configured action is performed without agent intervention.
- Customer rates the service → the rating contributes to quality reporting.
- Inbound reply mail contains quoted history beyond a configured delimiter → the redundant quoted content is trimmed so the request conversation stays readable.
- Supplier branding asset ages beyond its retention period → it is refreshed.

### 5.4 Business Rules

**Setup and readiness rules (enforced by the distribution):**

1. Setup may not proceed unless the operating platform meets the minimum supported generation, the capabilities required to process email are present, the permitted processing time allowance is at least thirty seconds, and the operating configuration and product configuration records are writable.
2. Where a required condition fails, the operator must be given a specific corrective instruction and a route to retry, not merely a failure.
3. Data-store connection details must be verified before they are used; unverified details must not be persisted.
4. A data store may be created during setup only when the operator has authorised creation.
5. Configuration changes made by the setup process are permitted only while the product is running in its non-live setup mode, and are refused otherwise.
6. The standard initial dataset — including the privilege levels the role model depends on — must be loaded before an administrator can be created.
7. Setup must not complete without establishing or confirming an active super administrator.
8. If an active super administrator already exists, setup must not create another.
9. If an account already exists for the supplied administrator email address, that account must be reused and, where necessary, elevated, rather than duplicated.
10. A newly created administrator account is enabled, treated as verified, and recorded as having originated from the website setup route.
11. A person may not hold two staff-level role instances; a customer-level identity may not be conflated with a staff-level identity.
12. Administrator identity data must satisfy these validation rules before it is accepted: name required and alphabetic; email address required and well formed; password required, confirmed by re-entry, at least eight characters, containing at least two letters, at least one digit, and at least one special character or underscore, and containing no whitespace.
13. The staff area address prefix and the customer area address prefix must both be supplied, must not be identical, and may contain only letters and numbers. Existing values must be read back to the operator as defaults.
14. Installation steps must be executed in the fixed order: configuration, structure migration, initial dataset, administrator creation, entry-address publication.

**Access rules:**

15. Only sign-in, account creation, password recovery, and credential update may be reached without authentication.
16. Staff and customers must authenticate separately and must land in their own area.
17. Administrative rights include agent rights; super-administrator rights include administrative rights; customer rights form a separate class outside the staff hierarchy.
18. Individual capabilities may be granted or withheld independently of the base privilege level.

**Support handling rules:**

19. A newly created request defaults to the organisation's standard classification — support type, open status, low priority — unless changed.
20. Requests progress through the recognised states of new, open, pending, answered, resolved, closed, with spam as a separate non-service disposition and trashed as a reversible removal preceding permanent deletion.
21. Internal notes are a distinct contribution type from customer-visible replies.
22. Requests may be assigned, reassigned, transferred, and forwarded, and collaborators may be added; each such change is recorded as an attributable event.
23. Requests may be filtered by attributes including identifier, status, priority, type, tag, source or channel, customer, agent, team, group, creation time, last reply time, and reply count; filters may be saved as reusable presets.

**Email and mailbox rules:**

24. Each mailbox is configured independently and may be enabled or disabled without affecting others; there is no limit on the number of mailboxes.
25. A mailbox may be configured to receive without sending, so inbound support mail can be accepted while outbound messaging from that mailbox is suppressed.
26. A stricter processing mode may be applied per mailbox.
27. Where reply-mail trimming is enabled, content below the configured delimiter is discarded so only the new reply is retained.
28. A support email address for the helpdesk is an operator-configurable setting.
29. Outbound messaging is inert until the organisation configures it; notifications therefore do not occur on an unconfigured installation.

**Content, attachment, and presentation rules:**

30. Attached material is limited per item, per submission, and in total per submission; material exceeding the limits must not be accepted.
31. Uploaded material is retained on the organisation's own storage by default.
32. Profile imagery must be supplied in the specified formats and dimensions.
33. Knowledge content visibility is governed by publication state; unpublished content is a draft and is not presented as self-service material.
34. Knowledge articles carry their own address identity and search-visibility metadata so they can be found through external search engines.
35. User-facing text is presented in the operator's selected language from the supported set, and each user may hold a personal language, timezone, and time-format preference.
36. The supplier branding asset is retained locally for a limited period and refreshed afterwards.

**Abuse-prevention rules:**

37. A human-verification challenge may be enabled and configured for public submissions; a submission that fails the challenge must be rejected and the user invited to retry.
38. Spam settings are separately administrable, and a request may be dispositioned as spam.

**Supplier registration rule:**

39. On completion of setup, or of the post-installation examination, the administrator's name and email address together with the organisation's site domain are transmitted to the supplier's registration service. Failure of this transmission must not prevent the organisation from completing its installation.

## 6. Business Requirements

Priorities: **M** = Must, **S** = Should, **C** = Could.

### 6.1 Acquisition, Deployment, and Environment Readiness

- **BR-DEP-01 (M)** — The organisation must be able to obtain the helpdesk through more than one route so that adoption is not blocked by its hosting circumstances: an automated dependency-managed install, a complete pre-packaged archive suitable for resource-constrained hosting, a containerised deployment, a supplier-provisioned cloud image, and a virtual-machine environment.
- **BR-DEP-02 (M)** — The organisation must be able to determine whether its environment is adequate **before** committing to installation, and must receive a specific corrective instruction for each unmet condition rather than a generic failure.
- **BR-DEP-03 (M)** — The helpdesk must refuse to install where the environment cannot support it, covering platform generation, the capabilities needed to process email, the permitted processing time allowance, and write access to operating and product configuration.
- **BR-DEP-04 (S)** — The organisation must be able to deploy the helpdesk as a self-contained unit that provisions its own records store and grants appropriate access when deployment credentials are supplied, and that reports clearly — without failing — when they are not.
- **BR-DEP-05 (S)** — The helpdesk must detect the presence of an external caching service during readiness verification and warn the operator to confirm its configuration, because a misconfigured cache can prevent access to support records.
- **BR-DEP-06 (M)** — The organisation must be able to operate the helpdesk entirely on infrastructure it controls, retaining custody of its support data.

### 6.2 Guided Setup and First-Run Configuration

- **BR-SET-01 (M)** — A non-specialist operator must be able to bring the helpdesk into service through a guided, step-by-step setup that requires no manual editing of product configuration.
- **BR-SET-02 (M)** — An equivalent terminal-based setup must be available so that the same outcome can be achieved where a browser-based setup is impractical, and so that an existing installation can be re-examined and corrected after deployment.
- **BR-SET-03 (M)** — The operator must be able to verify the organisation's records-store connection during setup and, where the intended store does not yet exist, authorise its creation; setup must not create a store without that authorisation and must stop with a clear message if the store is absent.
- **BR-SET-04 (M)** — Setup must bring the support-record structure to the current version and must warn the operator that this may take several minutes before proceeding.
- **BR-SET-05 (M)** — Setup must load the standard initial dataset so that the helpdesk starts with the privilege levels, classifications, and reference data its operating rules depend on.
- **BR-SET-06 (M)** — Setup must publish and display to the operator the separate staff and customer entry addresses on completion, so that the organisation knows immediately how to reach each area.
- **BR-SET-07 (M)** — The operator must be able to see progress through each installation step, and must be able to recover from a failed step by retrying without restarting the whole installation.
- **BR-SET-08 (M)** — Setup-time configuration changes must be refused once the helpdesk is in live operation, so that a production support service cannot be reconfigured inadvertently through the installer.
- **BR-SET-09 (S)** — The operator must be able to re-run a setup examination at any time to confirm that connectivity, record structure, initial dataset, and administrator presence are all still healthy, and to be offered correction of each deficiency found.
- **BR-SET-10 (S)** — The organisation must be able to control operating parameters that affect service behaviour — including how long a user session persists and how long a staff member may remain signed in — without supplier involvement.

### 6.3 First Administrator, Identity, and Access Governance

- **BR-GOV-01 (M)** — Setup must establish exactly one active administrator holding the highest privilege level, so that the organisation always has an accountable owner and never acquires a second one by accident.
- **BR-GOV-02 (M)** — Where a person already holds an account under the supplied email address, that account must be reused and elevated rather than duplicated, so that identity remains singular.
- **BR-GOV-03 (M)** — Administrator identity data must be validated before acceptance: name present and alphabetic; email address present and well formed; password present, confirmed, of adequate length and composition, and free of whitespace.
- **BR-GOV-04 (M)** — The helpdesk must maintain a graded staff privilege model in which administrative rights include agent rights and the highest level includes administrative rights, and must keep customer identity as a separate class outside the staff hierarchy.
- **BR-GOV-05 (M)** — A person must be prevented from holding two staff-level role instances, so that privilege cannot accumulate unintentionally on one identity.
- **BR-GOV-06 (M)** — Staff and customers must sign in through separate entry points and must arrive in their own area — staff at the staff dashboard, customers at their own request list.
- **BR-GOV-07 (M)** — Only sign-in, account creation, password recovery, and credential update may be reachable without authentication; all other capability must require an authenticated identity.
- **BR-GOV-08 (S)** — Individual capabilities must be grantable or withholdable independently of the base privilege level, so that duties such as managing a group's saved replies, agent activity, or announcements can be delegated without granting full administration.
- **BR-GOV-09 (S)** — Integrating systems must authenticate through a credential mechanism separate from interactive sign-in, so that machine access can be governed and revoked independently of human accounts.
- **BR-GOV-10 (S)** — The organisation must be able to maintain the population of agents and customers, including creating, updating, and removing them, with each such change recorded.
- **BR-GOV-11 (S)** — Each user must be able to hold personal preferences for language, timezone, and time format, and to maintain their own profile details and image.

### 6.4 Public Addressing and Channel Separation

- **BR-CHN-01 (M)** — The organisation must be able to choose the public address prefix for its staff area and for its customer area, so that each can be published under an identity appropriate to its audience.
- **BR-CHN-02 (M)** — The two address prefixes must both be supplied, must not be identical, and must contain only letters and numbers; existing values must be offered back to the operator as defaults.
- **BR-CHN-03 (S)** — Public addresses must carry the language in use, so that a visitor reaches the helpdesk in the correct language.
- **BR-CHN-04 (S)** — The organisation must be able to change its public addressing without supplier involvement.

### 6.5 Support Request Capture and Handling

- **BR-TKT-01 (M)** — Customers must be able to raise a support request and must be able to see and track the requests they have raised.
- **BR-TKT-02 (M)** — Every support request must be recorded as a managed, individually identifiable record with a subject, a requester, an origin channel, and a creation time.
- **BR-TKT-03 (M)** — A new request must be classified by type, status, and priority, defaulting to the organisation's standard classification so that no request is left unclassified.
- **BR-TKT-04 (M)** — Requests must progress through recognised states — new, open, pending, answered, resolved, closed — with spam as a separate non-service disposition, so that service position is unambiguous to staff and customers.
- **BR-TKT-05 (M)** — A request must hold a threaded conversation in which agent replies, customer replies, and collaborator replies are distinguishable, and in which internal notes are kept separate from customer-visible content.
- **BR-TKT-06 (M)** — Requests must be assignable to an individual agent and routable to a group or team, and must be transferable and forwardable between handlers.
- **BR-TKT-07 (M)** — Additional people must be addable to a request as collaborators so that others with a legitimate interest can follow and contribute.
- **BR-TKT-08 (S)** — Agents must be able to organise their workload through standard views — their own requests, unassigned, unanswered, starred, trashed — and to filter requests by identifier, status, priority, type, tag, source, customer, agent, team, group, creation time, last reply time, and reply count.
- **BR-TKT-09 (S)** — Frequently used filter combinations must be savable as reusable presets so that recurring triage work is not repeated manually.
- **BR-TKT-10 (S)** — Requests and individual contributions must be editable, pinnable, starable, and removable, with removal to a recoverable trash preceding permanent deletion.
- **BR-TKT-11 (S)** — Requests must be taggable with multiple tags and labelable, and the organisation must be able to define its own ticket types, so that the helpdesk reflects the organisation's own service categories.
- **BR-TKT-12 (M)** — Requests and conversation content must be searchable and sortable so that history can be found quickly.
- **BR-TKT-13 (M)** — Every significant change to a request — reply, note, priority, status, type, assignment, group, team, collaborator addition, transfer, deletion — must be recorded as an attributable event so that the handling history is auditable.

### 6.6 Email-Based Support Intake and Notification

- **BR-MAIL-01 (M)** — Support email sent to the organisation's support addresses must be converted into managed support requests so that email contact does not remain outside the helpdesk.
- **BR-MAIL-02 (M)** — The organisation must be able to register an unlimited number of mailboxes, each independently enabled or disabled, with its own inbound retrieval and outbound sending settings and sender identity.
- **BR-MAIL-03 (S)** — A mailbox must be configurable to receive without sending, so that inbound support mail can be accepted while outbound messaging from that mailbox is suppressed.
- **BR-MAIL-04 (S)** — Redundant quoted history must be removable from inbound replies using a configured delimiter, so that a request conversation remains readable and does not accumulate duplicated text.
- **BR-MAIL-05 (M)** — The organisation must be able to send email notifications to customers and to staff as part of request handling, and must be able to define the templates used for those notifications.
- **BR-MAIL-06 (M)** — The helpdesk's own support email address must be an operator-configurable setting.
- **BR-MAIL-07 (M)** — Outbound messaging must remain inert until the organisation configures it, so that no message is dispatched through an unintended channel; the organisation must be made aware that notification will not occur until configuration is complete.
- **BR-MAIL-08 (S)** — A stricter inbound processing mode must be selectable per mailbox for organisations that need tighter control over what is accepted.

### 6.7 Customer Self-Service and Knowledge

- **BR-KB-01 (S)** — Customers must be able to help themselves through published knowledge content, reducing the need to raise a request for routine questions.
- **BR-KB-02 (S)** — Knowledge content must be organised into a hierarchy of folders, categories, and articles so that customers can navigate to what they need.
- **BR-KB-03 (M)** — Knowledge authors must be able to control whether content is a draft or published, so that incomplete material is never presented as self-service guidance.
- **BR-KB-04 (S)** — Articles must carry their own address identity and search-visibility metadata, so that self-service content can be found through external search engines and thereby deflect contact before it reaches the organisation.
- **BR-KB-05 (S)** — Authors must be able to relate articles to one another so that a customer who has found one article can be guided to the next relevant one.
- **BR-KB-06 (S)** — Customers must be able to search the helpdesk's published content effectively.

### 6.8 Agent Productivity and Automation

- **BR-AUT-01 (S)** — The organisation must be able to define automation rules that evaluate conditions against request and message attributes and perform actions without agent intervention, so that repetitive routing and notification steps do not consume agent time.
- **BR-AUT-02 (S)** — Automation conditions must be expressible using ordinary business comparisons — equals, does not equal, contains, does not contain, starts with, ends with, before, after — against attributes such as sender and recipient address.
- **BR-AUT-03 (S)** — Automation actions must include notifying a user, notifying a customer, and transferring requests.
- **BR-AUT-04 (S)** — Agents must be able to reuse prepared responses and saved replies so that frequent questions are answered consistently and quickly; saved replies must be manageable at group level.
- **BR-AUT-05 (S)** — The organisation must be able to build its own forms and custom fields, including text, multi-line text, choice, single-choice, multi-choice, date, and date-and-time inputs, so that it can collect the information its own service processes require.
- **BR-AUT-06 (C)** — The organisation must be able to broadcast messages and publish announcements and advertisements with promotional text, promotional tags, tag colouring, and destination links, so that it can communicate proactively with its user population.

### 6.9 Workforce Organisation and Service Insight

- **BR-WFM-01 (S)** — The organisation must be able to structure its support workforce into groups and teams and to associate agents with them, so that work can be routed by organisational unit.
- **BR-WFM-02 (S)** — There must be no imposed ceiling on the number of agents, groups, teams, customers, or requests, so that the helpdesk can scale with the organisation without renegotiation.
- **BR-WFM-03 (S)** — Management must be able to monitor agent activity, including responsiveness measures such as last agent reply, so that service performance is visible.
- **BR-INS-01 (S)** — Management must be able to review reports and analytics covering workload and workflow, in order to improve the customer experience.
- **BR-INS-02 (S)** — Customers must be able to rate the service they received, and those ratings — including kudos — must contribute to quality reporting.
- **BR-INS-03 (S)** — Management must be able to define the periods over which activity is reported.

### 6.10 Branding, Customisation, and Extension

- **BR-EXT-01 (S)** — The organisation must be able to apply its own brand identity — logo, favicon, company information, and helpdesk details — so that the helpdesk presents as the organisation's own service.
- **BR-EXT-02 (M)** — The organisation must be able to install additional applications into a dedicated extension location without replacing the helpdesk, so that the product can be tailored to organisational needs.
- **BR-EXT-03 (C)** — The organisation must be able to discover and obtain further applications from the supplier's marketplace, including commercially licensed ones.
- **BR-EXT-04 (C)** — The organisation must be able to bring eCommerce order detail into its support requests from external selling platforms, so that agents handle order-related enquiries with the order context in front of them.
- **BR-EXT-05 (M)** — The organisation must be able to customise the product's own behaviour and appearance without voiding its ability to receive product updates.

### 6.11 Multilingual and Regional Operation

- **BR-LOC-01 (M)** — The helpdesk must operate in multiple languages, so that both customers and agents can use it in a language they understand. The distribution supports twelve languages: English, French, Italian, German, Danish, Arabic, Spanish, Turkish, Chinese, Polish, Hebrew, and Brazilian Portuguese.
- **BR-LOC-02 (S)** — Each user must be able to select a personal language, timezone, and time format, so that times and text are presented in that user's own conventions.
- **BR-LOC-03 (S)** — All user-facing text must be held separately from the product so that translations can be completed, corrected, and extended without altering the product itself.
- **BR-LOC-04 (S)** — The organisation must be able to select a default language for its helpdesk.

### 6.12 Content, Attachment, and Asset Handling

- **BR-ATT-01 (M)** — Customers and agents must be able to attach material to requests and replies, so that evidence and context travel with the request.
- **BR-ATT-02 (M)** — Attachment volume must be bounded per item, per submission, and in total per submission, so that the service remains usable and storage consumption remains predictable; material exceeding the limits must be rejected.
- **BR-ATT-03 (M)** — Uploaded material must be retained on the organisation's own storage by default, so that custody of customer-supplied content remains with the organisation.
- **BR-ATT-04 (S)** — Users must be able to upload and remove a profile image within the specified format and dimension rules.
- **BR-ATT-05 (S)** — Supplier-supplied branding assets must be held locally for a limited retention period and refreshed afterwards, so that presentation remains current without repeated external retrieval.

### 6.13 Protection Against Abuse

- **BR-ABU-01 (M)** — The organisation must be able to require a human-verification challenge on public submissions, and to enable, configure, and disable it, so that automated abuse of public support forms can be prevented.
- **BR-ABU-02 (M)** — A submission that fails the human-verification challenge must be rejected and the submitter invited to retry.
- **BR-ABU-03 (S)** — The organisation must be able to administer spam settings separately and to disposition a request as spam, so that junk contact does not consume agent capacity or pollute service reporting.

### 6.14 Supplier Registration and Product Stewardship

- **BR-REG-01 (M)** — The supplier requires each completed installation to be registered, carrying the administrator's name and email address and the organisation's site domain, so that adoption of the community edition is visible to the supplier.
- **BR-REG-02 (M)** — Failure of the registration transmission must not prevent the organisation from completing its installation or using its helpdesk.
- **BR-REG-03 (M)** — The organisation must be able to determine what personal data leaves its environment during installation and on what basis; the current implementation does not establish that the operator is informed of, or able to decline, the registration transmission. *(Open requirement — see §8.3.)*

### 6.15 Community, Contribution, and Security Stewardship

- **BR-COM-01 (S)** — Users must have distinct, structured routes for reporting a defect, requesting a feature, and asking a support question, so that each kind of contact reaches the right handling process.
- **BR-COM-02 (M)** — Security vulnerabilities must be disclosable privately to the supplier and must not be disclosed publicly, so that adopters are not exposed before a remedy exists.
- **BR-COM-03 (S)** — Contributors must be able to propose changes through a review process, with each change associated to the issue it addresses, and must be directed to the correct product component when the change belongs elsewhere.
- **BR-COM-04 (C)** — The project must be able to receive voluntary financial support, and must acknowledge backers and sponsors.
- **BR-COM-05 (S)** — Adopters must be able to obtain help through community channels independent of the supplier's commercial support.

### 6.16 Licensing and Distribution

- **BR-LIC-01 (M)** — The organisation must be able to determine unambiguously under what terms it may use, modify, and redistribute the product and its included components. The repository currently states conflicting terms and this must be resolved by the supplier. *(Open requirement — see §8.3.)*
- **BR-LIC-02 (M)** — The organisation must be able to adopt the product without licence cost for the community edition, while recognising that some marketplace extensions are commercially licensed.
- **BR-LIC-03 (S)** — The organisation must be able to identify the product version and the changes introduced in each release, so that upgrades can be planned.

## 7. Business Constraints and Policies

### 7.1 Business Constraints

- **Self-hosting.** The helpdesk operates on infrastructure the organisation provides and administers; the organisation carries the operational responsibility for availability, backup, and upkeep.
- **Single supported records platform.** The setup process supports only one family of relational data store and cannot provision or connect an alternative records platform, so an organisation standardised elsewhere must either adopt the supported platform or obtain supplier support.
- **Minimum environment.** Published requirements specify a modern server operating environment with adequate memory, a supported web-serving platform, a supported records platform version, a current platform generation, and email-processing capability present. The readiness check enforces a materially lower platform generation than the published requirement, so passing setup does not guarantee a supported environment.
- **Processing time allowance.** The environment must permit long-running operations of at least thirty seconds, because installation and structure updates are lengthy.
- **Attachment limits.** Uploaded material is bounded per item, per submission, and in total, and cannot be raised through the setup experience.
- **Session parameters.** Session duration is an operating parameter with a supplied default; staff may remain signed in for up to seven days.
- **Setup-mode restriction.** Configuration changes made through the guided setup are only permitted while the product runs in non-live setup mode, so a production installation cannot be reconfigured by that route.
- **Extension location.** Additional applications must reside in the product's dedicated extension location to be recognised.
- **Supported languages.** Operation is limited to the twelve shipped languages; serving a population outside that set requires additional translation work.

### 7.2 Policies

- **Administrator accountability.** An installation must have an active administrator at the highest privilege level; setup establishes or confirms one and will not create a duplicate.
- **Privilege separation.** Customer identity is kept outside the staff privilege hierarchy, and one person may not accumulate two staff-level role instances.
- **Authenticated access.** All capability other than sign-in, account creation, password recovery, and credential update requires authentication.
- **Internal versus customer-visible content.** Internal notes are maintained separately from customer-visible conversation.
- **Publication control.** Knowledge content is not presented as self-service guidance until published.
- **Recoverable deletion.** Removal of a request passes through a recoverable trash state before permanent deletion.
- **Attributable change.** Significant changes to requests and to the agent and customer population are recorded as attributable events.
- **Consent for record creation.** A records store is created during setup only on the operator's explicit authorisation.
- **Private security disclosure.** Security vulnerabilities are reported privately to the supplier and not published.
- **Contribution routing.** Changes are proposed through review and are directed to the product component that owns the behaviour.

### 7.3 Regulatory / Legal Constraints

- **Conflicting licence declaration.** The distribution's machine-readable metadata declares a permissive licence, while the shipped licence text and the published user documentation state a more restrictive reciprocal open-source licence for the included components. Until the supplier resolves this, the organisation's rights to modify, combine, and redistribute the product and its derivatives are legally uncertain. This is a material adoption constraint, particularly for organisations that intend to redistribute a customised helpdesk.
- **Personal data transmission at installation.** Completing setup transmits an identified individual's name and email address together with the organisation's site domain to a supplier-operated service outside the organisation's control. Organisations subject to data-protection obligations must establish a lawful basis, assess whether the individual has been informed, and determine whether an opt-out exists. The inspected implementation does not establish an informed-consent or opt-out mechanism.
- **Personal data held in the helpdesk.** The product holds identifiable information about customers, agents, and collaborators — including names, email addresses, contact numbers, profile images, conversation content, and attachments — for as long as the organisation retains its records. The distribution does not establish retention periods, erasure handling, or data-subject request handling; these obligations fall to the adopting organisation and are not addressed by the repository.
- **Cross-border transfer.** Registration data is sent to a supplier-operated service, and supplier branding assets are retrieved from an external location; organisations with data-residency requirements must assess both flows.
- **Commercial extension terms.** Marketplace applications carry their own commercial terms, separate from the community edition.

### 7.4 Organizational Constraints

- The product is maintained by an open-source community led by the supplier; continuity of the community edition, of its separately maintained operational components, and of third-party marketplace applications is not within the adopting organisation's control.
- The organisation must supply its own outbound messaging arrangement; none is provided.
- The organisation must supply and administer its own records platform and storage.
- Specialist effort is required for platform preparation, permission and ownership configuration, and upgrade planning.
- Serving a language outside the shipped set, or replacing the supported records platform, requires development effort beyond configuration.

## 8. Assumptions and Dependencies

### 8.1 Assumptions

1. The organisation intends to operate its support function on infrastructure it controls and accepts the operational responsibility that follows.
2. An administrator or operator with sufficient technical access is available to prepare the environment and complete setup.
3. The organisation has, or will obtain, a records platform of the supported family and an outbound messaging arrangement.
4. The organisation's support model is request-based — a customer raises an issue, staff work it to resolution — which is the model the product's states, roles, and events express.
5. The capability vocabulary shipped with the distribution reflects the capability set the assembled product presents to users; the distribution enables and configures those capabilities rather than implementing all of their detailed behaviour itself.
6. Detailed operational behaviour — request lifecycle mechanics, automation evaluation, mailbox processing, reporting calculation, knowledge-base presentation — is delivered by separately maintained product components that the distribution registers and enables.
7. Release history indicates an actively maintained product, though the recorded changes for the most recent release line are limited in scope.
8. The organisation will define its own quantitative service targets; none are supplied.

### 8.2 Dependencies

**Internal to the distribution:**

- The guided setup depends on the readiness checks passing, on verified records-store connectivity, on structure migration completing, on the initial dataset being loaded (which supplies the privilege levels the role model requires), and on administrator identity validation succeeding — in that fixed order.
- Administrator creation depends on the privilege levels existing in the initial dataset.
- Publication of staff and customer entry addresses depends on both prefixes being valid and distinct.
- Access governance depends on the configured address prefixes, since staff and customer areas are distinguished by them.
- Post-installation examination depends on records-store connectivity and can create an administrator only where the privilege levels exist.

**External:**

- Separately maintained product components supply core helpdesk behaviour, support-centre portal behaviour, email-to-request intake, automation, extension support, and programmatic access.
- The supplier's registration service must be reachable for installation registration; unreachability must not block installation.
- The supplier's external asset location supplies branding imagery.
- The supplier's marketplace supplies optional and commercial extensions, including eCommerce order synchronisation.
- The organisation's inbound mailboxes and outbound messaging provider.
- An external human-verification service, where challenge protection is enabled.
- Community and supplier support channels for defects, features, questions, and security disclosure.

### 8.3 Risks Affecting Business Requirements

| Risk | Effect on business requirements | Status |
|---|---|---|
| Conflicting licence declarations | BR-LIC-01 cannot be satisfied; adoption and redistribution rights are uncertain | Unresolved contradiction in the repository; requires supplier clarification |
| Installation transmits identified personal data externally with no established consent or opt-out | BR-REG-03 unmet; data-protection exposure for the adopting organisation | Open; requires supplier clarification or organisational mitigation |
| Readiness check accepts a lower platform generation than published requirements | BR-DEP-02/03 weakened; an organisation may pass setup on an unsupported environment | Contradiction confirmed in the repository |
| Shipped example operating-configuration template does not match the settings setup consumes, and states an older product version | Operators may configure settings with no effect; BR-DEP-01 and BR-SET-01 degraded | Contradiction confirmed in the repository |
| Outbound messaging inert by default | BR-MAIL-05/07; notifications silently absent on a fresh installation | Confirmed; requires operator action and clear operator notification |
| Detailed operational behaviour resides outside the distribution | Requirements in §6.5–§6.11 are enabled rather than directly evidenced end-to-end here; their precise rules must be confirmed against the responsible components | Scope limitation of this analysis |
| Records-platform lock-in | BR-DEP-06 satisfied but organisational platform standards may conflict | Constraint |
| Dependency on community and marketplace continuity | BR-EXT-02/03/04 and long-term supportability at risk | External dependency |
| Quantitative service targets absent | BR-INS-01/02 and §3.3 operational measures cannot be accepted objectively without organisational targets | Gap |
| Data retention, erasure, and data-subject request handling not established | Regulatory obligations fall entirely on the adopting organisation | Gap |

## 9. Business-Level Acceptance Criteria

### 9.1 Outcome Criteria

The helpdesk is acceptable when:

1. An operator following the published guidance can take the product from acquisition to a working installation without editing product configuration by hand.
2. Every readiness condition is reported individually, with a specific corrective instruction and a retry route when unmet, and installation cannot proceed while any are unmet.
3. The organisation's records store is verified reachable; it is created only when the operator authorised creation; and setup stops with a clear message when it is absent and unauthorised.
4. The support-record structure is current and the standard initial dataset is present after installation.
5. Exactly one active highest-privilege administrator exists, created from validated identity data, reusing rather than duplicating an existing account for the same email address.
6. The staff and customer areas are reachable at distinct, valid, operator-chosen addresses, and both are displayed to the operator on completion.
7. Staff and customers sign in separately and arrive in their own area; nothing beyond sign-in, account creation, password recovery, and credential update is reachable unauthenticated.
8. A request raised by a customer and a request arising from inbound support mail both become managed records with the organisation's default classification, and both progress through the recognised states.
9. Agent replies, customer replies, collaborator replies, and internal notes are distinguishable on a request, and every significant change is recorded as an attributable event.
10. No outbound message is dispatched before the organisation configures messaging, and messages are dispatched through the organisation's configured arrangement afterwards.
11. Published knowledge content is visible to customers and draft content is not.
12. Attachments exceeding the stated limits are rejected; accepted material is retained on the organisation's own storage.
13. The interface presents correctly in each supported language, and personal language, timezone, and time-format preferences are honoured.
14. A public submission that fails the enabled human-verification challenge is rejected with an invitation to retry.
15. Installation completes even when supplier registration cannot be transmitted.

### 9.2 Process Criteria

1. Setup steps execute in the fixed order — configuration, structure migration, initial dataset, administrator creation, address publication — with visible progress and per-step failure recovery.
2. Setup-time configuration changes are refused once the product is in live operation.
3. The post-installation examination can be re-run at any time and offers correction for each deficiency it finds.
4. A person cannot accumulate two staff-level role instances, and a customer identity cannot be conflated with a staff identity.
5. Removal of a request passes through a recoverable state before permanent deletion.
6. Defects, feature requests, support questions, contributions, and security disclosures each follow their own defined route, with security disclosure kept private.
7. Additional applications are recognised only when installed in the dedicated extension location.

### 9.3 Stakeholder Acceptance

- **Installing operator** accepts when readiness results are actionable, failures are recoverable, and completion yields known entry addresses and a working administrator account.
- **Super administrator** accepts when privilege levels, granular capabilities, groups, teams, branding, ticket types, custom fields and forms, mailbox settings, spam settings, email templates, and language defaults are all configurable without supplier involvement.
- **Support management** accepts when workload can be routed and filtered, saved views reduce repeated triage, and activity, reporting, and rating information make service performance visible.
- **Agents** accept when requests are findable, conversation and notes are clearly separated, prepared content is reusable, and transfer and collaboration work as expected.
- **Customers** accept when they can raise a request with attachments, track its state and conversation, reply, add collaborators, consult self-service content, and rate the service.
- **Privacy / compliance reviewer** accepts when the personal data transmitted outside the organisation is identified, justified, and — where required — able to be declined, and when the licence position is unambiguous. **On current evidence this acceptance is not achievable** without supplier clarification.
- **Supplier** accepts when completed installations are registered with administrator identity and site domain.

## 10. Traceability

### 10.1 Business Objectives to Business Requirements

| Objective | Requirements |
|---|---|
| G1 — Bring a complete support operation into service quickly and repeatably | BR-DEP-01…06; BR-SET-01…10 |
| G2 — Every request captured as a managed, trackable record | BR-TKT-01…13; BR-MAIL-01…08; BR-ATT-01…05 |
| G3 — Separate staff and customer environments | BR-GOV-01…11; BR-CHN-01…04 |
| G4 — Reduce repeat and low-value effort | BR-KB-01…06; BR-AUT-01…06; BR-ABU-01…03 |
| G5 — Shape the operation around the organisation | BR-EXT-01…05; BR-TKT-11; BR-AUT-05; BR-CHN-01…04 |
| G6 — Visibility of workload, responsiveness, sentiment | BR-WFM-01…03; BR-INS-01…03; BR-TKT-13 |
| G7 — Serve users in their own language and conventions | BR-LOC-01…04 |
| G8 — Extend without replacing | BR-EXT-01…05 |
| G9 — Sustainable open-source stewardship | BR-COM-01…05; BR-LIC-01…03; BR-REG-01…03 |

### 10.2 Stakeholder Needs to Business Requirements

| Stakeholder need | Requirements |
|---|---|
| Operator: know readiness, recover from failure, finish with a working system | BR-DEP-02/03; BR-SET-01…07, BR-SET-09 |
| Organisation: custody of data, own branding, no lock-out from extension | BR-DEP-06; BR-ATT-03; BR-EXT-01/02/05; BR-CHN-01…04 |
| Management: define permissions, organise staff, route work, see performance | BR-GOV-04/05/08/10; BR-WFM-01…03; BR-INS-01…03; BR-TKT-06/08/09 |
| Agents: find work, respond consistently, keep notes internal, hand over | BR-TKT-05/06/08/09/12; BR-AUT-04 |
| Customers: raise, track, reply, involve others, self-serve, rate | BR-TKT-01/02/04/05/07; BR-KB-01…06; BR-INS-02; BR-ATT-01 |
| Knowledge authors: organise, control visibility, be discoverable | BR-KB-02…05 |
| API consumers: governed machine access | BR-GOV-09 |
| Mail system: inbound intake and outbound notification control | BR-MAIL-01…08 |
| Supplier: adoption visibility, asset distribution, extension marketplace | BR-REG-01/02; BR-ATT-05; BR-EXT-03 |
| Community: structured defect, feature, question, contribution, funding routes | BR-COM-01…05 |
| Privacy reviewer: know and control data leaving the organisation | BR-REG-03; §7.3 |

### 10.3 Business Requirements to Downstream Requirements

| Business requirement area | Downstream specification required |
|---|---|
| BR-DEP, BR-SET | Software requirements for readiness evaluation, records-store provisioning, structure migration, initial dataset loading, configuration writing, and setup-mode restriction; deployment and environment specifications |
| BR-GOV, BR-CHN | Software requirements for the privilege hierarchy, granular capability grants, separate authentication channels, session and remember-me duration, address-prefix validation and publication, and programmatic-access credentials |
| BR-TKT | Software requirements for the request data model, state machine, threading, note separation, assignment/transfer/forwarding, collaboration, tagging and typing, filtering and saved presets, search and sort, and event recording |
| BR-MAIL | Software requirements for mailbox registration and enablement, inbound retrieval, outbound sending and suppression, delimiter trimming, strict mode, and notification templating |
| BR-KB | Software requirements for content hierarchy, publication states, address identity and search-visibility metadata, article relationships, and content search |
| BR-AUT | Software requirements for rule conditions and actions, prepared content, and custom form and field definitions |
| BR-WFM, BR-INS | Software requirements for organisational units, activity capture, reporting periods, and rating/kudos capture |
| BR-EXT | Software requirements for the extension location and lifecycle, marketplace discovery, and external order synchronisation |
| BR-LOC | Software requirements for the supported language set, externalised text management, personal preferences, and language-aware public addressing |
| BR-ATT | Software requirements for attachment limits, rejection handling, storage custody, profile imagery rules, and branding-asset retention |
| BR-ABU | Software requirements for challenge enablement and configuration, challenge failure handling, and spam administration and disposition |
| BR-REG | Software requirements for registration content and transmission, non-blocking failure behaviour, and any consent or opt-out mechanism once clarified |
| BR-COM, BR-LIC | Process and governance specifications for issue routing, private security disclosure, contribution review, funding, release communication, and licence resolution |

## 11. References

**Product and distribution**

- UVdesk Community Helpdesk project skeleton — product description, capability list, published environment requirements, acquisition routes, staff and customer entry-address conventions, module and marketplace references, and licensing statement.
- Installation guide — environment preparation, platform and permission guidance, and installation route.
- Release notes for the 1.0, 1.1, and 1.2 release lines.
- Product licence text.
- Distribution metadata, including declared licence and the assembled component set.

**Setup and configuration**

- Guided browser-based setup: readiness evaluation, records-store verification, administrator identity capture, entry-address configuration, installation sequencing and progress, and validation rules.
- Terminal-based setup and post-installation examination: connectivity verification and interactive re-configuration, structure currency, initial dataset, administrator creation, and installation registration.
- Administrator creation rules: role resolution, account reuse and elevation, staff/customer role-instance exclusivity.
- Operating-configuration update behaviour and its restriction to non-live operation.
- Product configuration: supported languages, entry-address prefixes, attachment limits, upload storage, support address, default request classification, and default notification template.
- Mailbox configuration: mailbox registration, enablement, outbound suppression, strict mode, inbound and outbound settings, and reply delimiter trimming.
- Extension configuration: dedicated application location.
- Access configuration: privilege hierarchy, separate staff/customer/programmatic channels, remember-me duration, and unauthenticated access scope.
- Environment configuration and the shipped example template, including messaging inert-by-default and session lifetime.
- Containerised deployment provisioning behaviour.

**Operational capability vocabulary**

- Shipped user-facing language set for English, evidencing request states and views, request attributes and operations, activity events, automation conditions and actions, workforce and privilege administration, knowledge-base structure and publication, form building and custom fields, branding and settings, reporting and ratings, announcements, application discovery and eCommerce order synchronisation, human-verification settings, and personal preferences.
- Additional shipped language sets for French, Italian, German, Danish, Arabic, Spanish, Turkish, Chinese, Polish, Hebrew, and Brazilian Portuguese.

**Community and stewardship**

- Contribution guidance; defect, feature-request, and support-question templates; change-proposal template; security disclosure policy; funding configuration.

**Open items requiring supplier or organisational resolution**

- Licence declaration conflict between distribution metadata and shipped licence text.
- Presence or absence of operator notification and opt-out for installation registration transmission.
- Reconciliation of the enforced minimum platform generation with the published environment requirements.
- Correction of the shipped example operating-configuration template to match consumed settings and current product version.
- Data retention, erasure, and data-subject request handling for customer, agent, and collaborator personal data.
- Quantitative service targets for the operational success measures in §3.3.

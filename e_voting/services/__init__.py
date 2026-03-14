"""
Services package — Business logic layer for the E-Voting system.

Each service class encapsulates the rules and operations for one
domain area. Services receive the DataStore via constructor injection
and never perform direct I/O (no printing, no input reading).

Service classes:
  AuthService       — Authentication and voter registration
  CandidateService  — Candidate CRUD and search
  StationService    — Voting station CRUD
  PollService       — Poll & position lifecycle management
  VoterService      — Admin-side voter management
  AdminService      — Admin account management
  VoteService       — Ballot casting and vote recording
  ResultService     — Result tallying, statistics, and reporting
"""

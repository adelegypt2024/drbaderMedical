CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TYPE "UserRole" AS ENUM ('admin', 'consultant', 'client');
CREATE TYPE "RequestStatus" AS ENUM ('OPEN', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED');
CREATE TYPE "ProposalStatus" AS ENUM ('PENDING', 'ACCEPTED', 'DECLINED');
CREATE TYPE "ContractStatus" AS ENUM ('DRAFT', 'ACTIVE', 'COMPLETED', 'CANCELLED');
CREATE TYPE "InvoiceStatus" AS ENUM ('OPEN', 'PAID', 'VOID');
CREATE TYPE "PaymentStatus" AS ENUM ('PENDING', 'SUCCEEDED', 'FAILED');
CREATE TYPE "FileCategory" AS ENUM ('REQUEST', 'CONTRACT', 'MESSAGE');

CREATE TABLE "Organization" (
  "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  "name" TEXT NOT NULL,
  "industry" TEXT,
  "createdAt" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "updatedAt" TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE "User" (
  "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  "email" TEXT NOT NULL UNIQUE,
  "password_hash" TEXT NOT NULL,
  "first_name" TEXT NOT NULL,
  "last_name" TEXT NOT NULL,
  "role" "UserRole" NOT NULL,
  "email_verified" BOOLEAN NOT NULL DEFAULT FALSE,
  "verification_token" TEXT UNIQUE,
  "reset_token" TEXT UNIQUE,
  "reset_token_expires" TIMESTAMPTZ,
  "created_at" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "updated_at" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "organization_id" UUID REFERENCES "Organization"("id")
);

CREATE TABLE "ConsultantProfile" (
  "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  "user_id" UUID NOT NULL UNIQUE REFERENCES "User"("id") ON DELETE CASCADE,
  "specialties" TEXT[] NOT NULL,
  "hourly_rate" DOUBLE PRECISION NOT NULL,
  "years_experience" INTEGER NOT NULL,
  "bio" TEXT,
  "availability" TEXT,
  "portfolio_url" TEXT,
  "created_at" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "updated_at" TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE "Service" (
  "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  "name" TEXT NOT NULL,
  "description" TEXT,
  "category" TEXT,
  "consultant_id" UUID REFERENCES "ConsultantProfile"("id") ON DELETE SET NULL
);

CREATE TABLE "Request" (
  "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  "title" TEXT NOT NULL,
  "description" TEXT NOT NULL,
  "category" TEXT NOT NULL,
  "budget" TEXT NOT NULL,
  "target_date" TIMESTAMPTZ NOT NULL,
  "status" "RequestStatus" NOT NULL DEFAULT 'OPEN',
  "created_at" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "updated_at" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "client_id" UUID NOT NULL REFERENCES "User"("id") ON DELETE CASCADE,
  "organization_id" UUID REFERENCES "Organization"("id") ON DELETE SET NULL,
  "service_id" UUID REFERENCES "Service"("id") ON DELETE SET NULL
);

CREATE TABLE "Proposal" (
  "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  "request_id" UUID NOT NULL REFERENCES "Request"("id") ON DELETE CASCADE,
  "consultant_id" UUID NOT NULL REFERENCES "User"("id") ON DELETE CASCADE,
  "scope" TEXT NOT NULL,
  "timeline" TEXT NOT NULL,
  "cost" DOUBLE PRECISION NOT NULL,
  "created_at" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "status" "ProposalStatus" NOT NULL DEFAULT 'PENDING'
);

CREATE TABLE "Contract" (
  "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  "proposal_id" UUID NOT NULL UNIQUE REFERENCES "Proposal"("id") ON DELETE CASCADE,
  "status" "ContractStatus" NOT NULL DEFAULT 'DRAFT',
  "effective_date" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "terms" TEXT NOT NULL
);

ALTER TABLE "Request" ADD COLUMN "contract_id" UUID UNIQUE REFERENCES "Contract"("id") ON DELETE SET NULL;

CREATE TABLE "Invoice" (
  "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  "contract_id" UUID NOT NULL REFERENCES "Contract"("id") ON DELETE CASCADE,
  "amount" DOUBLE PRECISION NOT NULL,
  "due_date" TIMESTAMPTZ NOT NULL,
  "status" "InvoiceStatus" NOT NULL DEFAULT 'OPEN',
  "created_at" TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE "Payment" (
  "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  "invoice_id" UUID NOT NULL REFERENCES "Invoice"("id") ON DELETE CASCADE,
  "payer_id" UUID NOT NULL REFERENCES "User"("id"),
  "payee_id" UUID NOT NULL REFERENCES "User"("id"),
  "amount" DOUBLE PRECISION NOT NULL,
  "status" "PaymentStatus" NOT NULL DEFAULT 'PENDING',
  "processed_at" TIMESTAMPTZ,
  "provider_ref" TEXT
);

CREATE TABLE "Message" (
  "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  "request_id" UUID NOT NULL REFERENCES "Request"("id") ON DELETE CASCADE,
  "author_id" UUID NOT NULL REFERENCES "User"("id") ON DELETE CASCADE,
  "body" TEXT NOT NULL,
  "created_at" TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE "Appointment" (
  "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  "title" TEXT NOT NULL,
  "start_time" TIMESTAMPTZ NOT NULL,
  "end_time" TIMESTAMPTZ NOT NULL,
  "timezone" TEXT NOT NULL,
  "request_id" UUID REFERENCES "Request"("id") ON DELETE SET NULL,
  "consultant_id" UUID REFERENCES "ConsultantProfile"("id") ON DELETE SET NULL,
  "participant_id" UUID REFERENCES "User"("id") ON DELETE SET NULL
);

CREATE TABLE "File" (
  "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  "request_id" UUID REFERENCES "Request"("id") ON DELETE SET NULL,
  "message_id" UUID REFERENCES "Message"("id") ON DELETE SET NULL,
  "uploader_id" UUID NOT NULL REFERENCES "User"("id") ON DELETE CASCADE,
  "category" "FileCategory" NOT NULL,
  "path" TEXT NOT NULL,
  "filename" TEXT NOT NULL,
  "mime_type" TEXT NOT NULL,
  "size_bytes" INTEGER NOT NULL,
  "created_at" TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE "Audit" (
  "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  "user_id" UUID REFERENCES "User"("id") ON DELETE SET NULL,
  "request_id" UUID REFERENCES "Request"("id") ON DELETE SET NULL,
  "contract_id" UUID REFERENCES "Contract"("id") ON DELETE SET NULL,
  "action" TEXT NOT NULL,
  "metadata" JSONB,
  "created_at" TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX "idx_request_client" ON "Request" ("client_id");
CREATE INDEX "idx_proposal_request" ON "Proposal" ("request_id");
CREATE INDEX "idx_message_request" ON "Message" ("request_id");
CREATE INDEX "idx_invoice_contract" ON "Invoice" ("contract_id");
CREATE INDEX "idx_payment_invoice" ON "Payment" ("invoice_id");

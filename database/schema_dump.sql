--
-- PostgreSQL database dump
--

-- Dumped from database version 15.4
-- Dumped by pg_dump version 15.4

-- Started on 2025-07-18 13:43:36

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 8 (class 2615 OID 16398)
-- Name: pgagent; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA pgagent;


ALTER SCHEMA pgagent OWNER TO postgres;

--
-- TOC entry 3496 (class 0 OID 0)
-- Dependencies: 8
-- Name: SCHEMA pgagent; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA pgagent IS 'pgAgent system tables';


--
-- TOC entry 2 (class 3079 OID 16384)
-- Name: adminpack; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS adminpack WITH SCHEMA pg_catalog;


--
-- TOC entry 3497 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION adminpack; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION adminpack IS 'administrative functions for PostgreSQL';


--
-- TOC entry 3 (class 3079 OID 16399)
-- Name: pgagent; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgagent WITH SCHEMA pgagent;


--
-- TOC entry 3498 (class 0 OID 0)
-- Dependencies: 3
-- Name: EXTENSION pgagent; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgagent IS 'A PostgreSQL job scheduler';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 244 (class 1259 OID 16562)
-- Name: attendance; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.attendance (
    id integer NOT NULL,
    attendance_of_record boolean NOT NULL,
    attendance_type boolean NOT NULL,
    block_name character varying,
    comment character varying,
    date character varying,
    excuse_category_description character varying,
    excuse_category_id integer NOT NULL,
    excuse_description character varying,
    excuse_type_id integer NOT NULL,
    excused integer NOT NULL,
    grad_year character varying,
    grade character varying,
    grade_level_sort integer NOT NULL,
    group_name character varying,
    photo_file_name character varying,
    section character varying,
    section_id integer NOT NULL,
    student_name character varying,
    student_user_id integer NOT NULL,
    teacher_name character varying
);


ALTER TABLE public.attendance OWNER TO postgres;

--
-- TOC entry 247 (class 1259 OID 27215)
-- Name: course_codes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.course_codes (
    transcript_category double precision,
    course_prefix character varying NOT NULL
);


ALTER TABLE public.course_codes OWNER TO postgres;

--
-- TOC entry 248 (class 1259 OID 27360)
-- Name: department_mappings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.department_mappings (
    transcript_category double precision NOT NULL,
    department character varying
);


ALTER TABLE public.department_mappings OWNER TO postgres;

--
-- TOC entry 249 (class 1259 OID 28596)
-- Name: enrollment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.enrollment (
    student_user_id integer NOT NULL,
    student_first character varying,
    student_last character varying,
    grad_year double precision,
    enroll_date character varying,
    depart_date character varying,
    graduated boolean,
    depart_year character varying,
    enroll_grade character varying,
    enroll_year character varying,
    graduated_status character varying,
    email character varying
);


ALTER TABLE public.enrollment OWNER TO postgres;

--
-- TOC entry 246 (class 1259 OID 26672)
-- Name: gpa; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.gpa (
    student_user_id integer NOT NULL,
    calculated_gpa double precision
);


ALTER TABLE public.gpa OWNER TO postgres;

--
-- TOC entry 251 (class 1259 OID 38313)
-- Name: parents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.parents (
    email character varying NOT NULL,
    first_name character varying,
    last_name character varying,
    grade integer[]
);


ALTER TABLE public.parents OWNER TO postgres;

--
-- TOC entry 250 (class 1259 OID 37712)
-- Name: transcript_comments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.transcript_comments (
    student_user_id integer NOT NULL,
    student_first character varying,
    student_last character varying,
    comment character varying,
    comment_insert_date character varying
);


ALTER TABLE public.transcript_comments OWNER TO postgres;

--
-- TOC entry 245 (class 1259 OID 24824)
-- Name: transcripts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.transcripts (
    student_user_id integer NOT NULL,
    student_first character varying,
    student_last character varying,
    grad_year double precision,
    course_title character varying,
    course_id integer NOT NULL,
    course_code character varying,
    group_description character varying,
    term_name character varying,
    grade_description character varying,
    grade_mode character varying,
    grade character varying,
    score double precision,
    transcript_category double precision,
    group_id integer NOT NULL,
    term_id integer NOT NULL,
    grade_id integer NOT NULL,
    school_year character varying,
    address_1 character varying,
    address_2 character varying,
    address_3 character varying,
    address_city character varying,
    address_state character varying,
    address_zip character varying
);


ALTER TABLE public.transcripts OWNER TO postgres;

--
-- TOC entry 3337 (class 2606 OID 26676)
-- Name: gpa GPA_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gpa
    ADD CONSTRAINT "GPA_pkey" PRIMARY KEY (student_user_id);


--
-- TOC entry 3333 (class 2606 OID 16568)
-- Name: attendance attendance_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_pkey PRIMARY KEY (id);


--
-- TOC entry 3341 (class 2606 OID 27366)
-- Name: department_mappings department_mappings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.department_mappings
    ADD CONSTRAINT department_mappings_pkey PRIMARY KEY (transcript_category);


--
-- TOC entry 3339 (class 2606 OID 27244)
-- Name: course_codes departments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.course_codes
    ADD CONSTRAINT departments_pkey PRIMARY KEY (course_prefix);


--
-- TOC entry 3343 (class 2606 OID 28602)
-- Name: enrollment enrollment_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.enrollment
    ADD CONSTRAINT enrollment_pkey PRIMARY KEY (student_user_id);


--
-- TOC entry 3347 (class 2606 OID 38319)
-- Name: parents parents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parents
    ADD CONSTRAINT parents_pkey PRIMARY KEY (email);


--
-- TOC entry 3345 (class 2606 OID 37718)
-- Name: transcript_comments transcript_comments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transcript_comments
    ADD CONSTRAINT transcript_comments_pkey PRIMARY KEY (student_user_id);


--
-- TOC entry 3335 (class 2606 OID 25166)
-- Name: transcripts transcripts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transcripts
    ADD CONSTRAINT transcripts_pkey PRIMARY KEY (student_user_id, term_id, group_id, course_id, grade_id);


--
-- TOC entry 3348 (class 2606 OID 27367)
-- Name: course_codes transcirpt_category_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.course_codes
    ADD CONSTRAINT transcirpt_category_fk FOREIGN KEY (transcript_category) REFERENCES public.department_mappings(transcript_category) NOT VALID;


-- Completed on 2025-07-18 13:43:36

--
-- PostgreSQL database dump complete
--


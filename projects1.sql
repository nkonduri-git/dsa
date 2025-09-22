---------- data cleaning
select *
from layoffs ;
#1.remove duplicates
#2.standradize the data
#3 null value or blank value 
#4.remove any coloums 

CREATE TABLE layoffs_staging
LIKE  layoffs;

select *
from layoffs_stagging;


INSERT layoffs_staging
select *
from layoffs;

with duplicate_cte as 
(
select *,# WE ARE USING THE ROW NUBER BECAUSE IT WILL GIVE THE UNIQUE NUMBER IF THERE IS DUPLICATE IT WILL INCREASE THE NUMBER STARTINGT FROM 1 
ROW_NUMBER() over(partition by company,location,total_laid_off,percentage_laid_off,stage,country,total_laid_off,percentage_laid_off,'date',funds_raised_millions) AS row_num
from layoffs_staging

)
SELECT*
FROM duplicate_cte
where row_num > 1 ;
#so to delete the duplicates one more table with same coloums taken and added the data which is of duplicate into it and delete the data from that table 

CREATE TABLE layoffs_staging2 (
  `company` text,
  `location` text,
  `industry` text,
  `total_laid_off` int DEFAULT NULL,
  `percentage_laid_off` text,
  `date` text,
  `stage` text,
  `country` text,
  `funds_raised_millions` int DEFAULT NULL,
   `row_num` INT 
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO layoffs_staging2 
select *,# WE ARE USING THE ROW NUBER BECAUSE IT WILL GIVE THE UNIQUE NUMBER IF THERE IS DUPLICATE IT WILL INCREASE THE NUMBER STARTINGT FROM 1 
ROW_NUMBER() over(partition by company,location,total_laid_off,percentage_laid_off,stage,country,total_laid_off,percentage_laid_off,'date',funds_raised_millions) AS row_num
from layoffs_staging;




Delete 
FROM layoffs_staging2
where row_num > 1 ;

#standardizing
select company , trim(company)
from layoffs_stagging2;

update layoffs_staging2
set company = trim(company);

select distinct industry
from layoffs_staging2
order by 1 ;

select  industry
from layoffs_staging2
where industry like 'crypto%';

update layoffs_staging2
set industry = 'crypto'
where industry like 'crypto%';

 #to check the co9loum first use the format 
 select distinct country
 from layoffs_stagging2
 order by 1;
 
UPDATE layoffs_staging2
set country = trim(trailing '.' from country)
where country like 'unitede states%';

select 'date',
str_to_date(`date`,'%m/%d/%Y')#coloum name followed by format we put the data 
from layoffs_staging2;
update layoffs_staging2
set `date`=str_to_date(`date`,'%m/%d/%Y');#coloum name followed by format we put the data 
Alter table layoffs_staging2
MODIFY COLUMN `date` date;
#working with the null
update layoffs_staging2
set industry = null
where industry = '';
select *
from layoffs_staging2
where total_laid_off is NULL
AND percentage_laid_off IS NULL;
select *
from layoffs_staging2
where industry is NULL
or insudtry = '';
select *
from layoffs_staging2 t1
join layoffs_staging2 t2
    ON t1.company = t2.company
where (t1.industry IS NULL )
and t2.industry is not null;

update layoffs_staging2 t1
join layoffs_staging2 t2
  on t1.company = t2.company 
set t1.industry = t2.insudtry #in null values we will create 2 tables 1 with null and other without null values then join them both 
where (t1.industry is null )
and t2.industry is not null;

DELETE 
from layoffs_staging2
where total_laid_off is null 
and percentage_laid_off is null ;

ALTER TABLE layoffs_staging2
drop column row_num;

# exploration

select max(total_laid_off),max(percentage_laid_off)
from layoffs_stagging2;

select *
from layoffs_staging2
where percentage_laid_off=1
order by funds_raised_millions desc;

select *
from layoffs_staging2
where percentage_laid_off=1
order by funds_raised_millions desc;

select *
from layoffs_staging2
where percentage_laid_off=1
order by funds_raised_millions desc;

select country, sum(total_laid_off)
from layoffs_staging2
group by country
order by 2 desc;
select country, sum(total_laid_off)
from layoffs_staging2
group by stage
order by 2 desc;


select substring('date',1,7) AS 'MONTH', sum(total_laid_off)
from layoffs_staging2
where substring('date',1,7) is not null
group by 'month'
order by 1 desc;

with rolling_total as
(
select substring('date',1,7) AS 'MONTH', sum(total_laid_off) AS total_off
from layoffs_staging2
where substring('date',1,7) is not null
group by 'month'
order by 1 desc
)
select 'month' ,sum(total_off) over(order by 'month')
from rolling_total;
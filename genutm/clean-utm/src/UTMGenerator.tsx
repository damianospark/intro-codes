import React, { useState } from "react";
// import { Button, TextField, Container, Typography, Box, Grid } from "@mui/material";
import { Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions, Button, TextField, Container, Typography, Grid, Box, SelectChangeEvent, IconButton } from "@mui/material";
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import useScrollTrigger from "@mui/material/useScrollTrigger";
import Slide from "@mui/material/Slide";
import CssBaseline from "@mui/material/CssBaseline";
import CakeSharpIcon from "@mui/icons-material/CakeSharp";
import Chip from "@mui/material/Chip";

import Autocomplete, { createFilterOptions } from "@mui/material/Autocomplete";
import { Api } from "nocodb-sdk";
import moment from "moment-timezone";
import EditableAutoSizedTable from "./EditableAutoSizedTable";
//TODO: 컴펙트하게 보이도록 입력 필드들 재 배치
// const burl = "http://better.cleanb.life:30008";
const burl = "https://better.cleanb.life:30009";

const api = new Api({
  baseURL: burl,
  headers: {
    "xc-auth": authToken,
  },
});

interface UTMParams {
  land_url: string;
  source: string;
  medium: string;
  campaign: string;
  term?: string;
  content?: string;
}

moment.locale("ko");
function toKSTISOString(date: Date): string {
  return moment(date).tz("Asia/Seoul").toISOString();
}
const sources = ["facebook", "instagram", "naver", "google", "daangn", "incruit", "jobkorea"];
const mediums = ["social", "blog", "search", "naver_power_ranking", "naver_shop_search", "naver_cafe", "influencer", "bulletin"];
const filter = createFilterOptions<string>();
const landing_url = "https://www.cleanbedding.kr/product/trial";

interface UTMGeneratorProps {
  user: string;
}

interface Props {
  /**
   * Injected by the documentation to work in an iframe.
   * You won't need it on your project.
   */
  window?: () => Window;
  children: React.ReactElement;
}

function HideOnScroll(props: Props) {
  const { children, window } = props;
  // Note that you normally won't need to set the window ref as useScrollTrigger
  // will default to window.
  // This is only being set here because the demo is in an iframe.
  const trigger = useScrollTrigger({
    target: window ? window() : undefined,
  });

  return (
    <Slide appear={false} direction="down" in={!trigger}>
      {children}
    </Slide>
  );
}

const UTMGenerator: React.FC<UTMGeneratorProps> = (props) => {
  const [rowId, setRowId] = useState(-1);
  const [utmParams, setUtmParams] = useState<UTMParams>({
    source: "",
    medium: "",
    campaign: "",
    term: "",
    content: "",
    land_url: landing_url,
  });
  const [generatedUrl, setGeneratedUrl] = useState("");

  const [openDialog, setOpenDialog] = useState(false);
  const [missingFields, setMissingFields] = useState<string[]>([]);

  const validateForm = () => {
    const requiredFields = ["land_url", "source", "medium", "campaign", "content"];
    const missing = requiredFields.filter((field) => !utmParams[field as keyof UTMParams]);
    setMissingFields(missing);
    return missing.length === 0;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement> | SelectChangeEvent<string>, param: keyof UTMParams) => {
    setUtmParams({ ...utmParams, [param]: e.target.value });
  };

  const handleChangeAutoComplete = (newValue: string | null, param: keyof UTMParams) => {
    if (newValue) {
      if (newValue.includes("Add ")) {
        newValue = newValue.replace("Add ", "").replaceAll('"', "");
      }
      console.log(param, newValue);
      setUtmParams({ ...utmParams, [param]: newValue });
    } else {
      setUtmParams({ ...utmParams, [param]: "" });
    }
  };
  const handleCloseDialog = () => {
    setOpenDialog(false);
  };
  const generateUTM = async () => {
    // const now: Date = moment(new Date()).toDate();
    // const twoWeeksFromNow: Date = moment(new Date()).add(2, "weeks").toDate();

    const now: string = moment(new Date()).format("YYYY-MM-DD");
    const twoWeeksFromNow: string = moment(new Date()).add(2, "weeks").format("YYYY-MM-DD");
    console.log("moment -> ", typeof now, now);
    // console.log("moment -> ", now, );
    // console.log(utmParams);
    if (!validateForm()) {
      setOpenDialog(true);
      return;
    }
    const encodedParams = Object.entries(utmParams)
      // .filter(([_, value]) => value)
      .filter(([key, value]) => key !== "land_url" && value)
      .map(([key, value]) => `utm_${key}=${encodeURIComponent(value.trim().replace(/\s+/g, "-"))}`)
      .join("&");
    const utm = `${utmParams.land_url}?${encodedParams}`;
    setGeneratedUrl(utm);

    await api.dbTableRow
      .create("noco", "UtmGenerator", "utm_data", {
        // Id: 0,
        // source: utmParams.source,
        // medium: utmParams.medium,
        // campaign: utmParams.campaign,
        // Term: utmParams.term,
        // content: "string",
        ...utmParams,
        utm: utm,
        post_url: "string",
        descr: "string",
        // created_at: moment(new Date()),
        // UpdatedAt: null,
        creator_id: props.user,
        updater_id: props.user,
        budget: 0,
        currency: "원",
        start_date: now,
        end_date: twoWeeksFromNow,
        target_location: null,
        target_audience: null,
      })
      .then(function (data) {
        setRowId(data.id);
        console.log("then data", data);
      })
      .catch(function (error) {
        // console.error("---error---", error);
        // console.error(error.response.data);
        console.error(error.response.data.info, error.response.data.message);
        console.error(error.response.data.info.message);
        alert(`데이터 삽입 오류가 발생했습니다.\n CODE:${error.response.data.info.code}\n MESSAGE: ${error.response.data.message}`);
      });
  };

  return (
    <React.Fragment>
      <CssBaseline />
      <HideOnScroll {...props}>
        <AppBar>
          <Toolbar>
            <Chip label={props.user} color="warning" size="medium" />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }} gutterBottom>
              Cleanbedding UTM 생성기
            </Typography>
            <IconButton size="large" aria-label="UTM track result" aria-controls="menu-appbar" aria-haspopup="true" onClick={() => alert("성과 확인 기능 추가 예정입니다.")} color="inherit">
              <CakeSharpIcon />
            </IconButton>
          </Toolbar>
        </AppBar>
      </HideOnScroll>
      <Toolbar />
      <Container sx={{ minWidth: "100%", paddingX: 0, paddingY: 2 }}>
        <Box mb={2}>
          <Grid container spacing={2}>
            <Grid item xs={5}>
              <TextField
                required
                focused
                color="secondary"
                label="랜딩페이지 URL"
                variant="outlined"
                fullWidth
                value={landing_url}
                // onChange={(e) => setUrl(e.target.value)}
                onChange={(e) => handleChange(e, "land_url")}
              />
            </Grid>
            <Grid item xs={7}>
              <Typography variant="body1" color="textSecondary" gutterBottom align="left">
                랜딩페이지의 url입력 (기본 값과 다를 경우 입력)
              </Typography>
            </Grid>
          </Grid>
        </Box>
        <Box mb={2}>
          <Grid container spacing={2}>
            <Grid item xs={5}>
              <Autocomplete
                options={sources}
                getOptionLabel={(option) => {
                  if (typeof option === "string") {
                    return option;
                  }
                  // Regular option
                  return "";
                }}
                filterOptions={(options, params) => {
                  const filtered = filter(options, params);

                  const { inputValue } = params;
                  // Suggest the creation of a new value
                  const isExisting = options.some((option) => inputValue === option);
                  if (inputValue !== "" && !isExisting) {
                    filtered.push(`Add "${inputValue}"`); //inputValue,
                  }

                  return filtered;
                }}
                freeSolo
                selectOnFocus
                value={utmParams.source}
                onChange={(e, newValue) => handleChangeAutoComplete(newValue, "source")}
                renderInput={(params) => (
                  <div>
                    {" "}
                    <TextField {...params} required focused color="secondary" label="Source" variant="outlined" fullWidth />{" "}
                  </div>
                )}
              />
            </Grid>
            <Grid item xs={7}>
              <Typography variant="body1" color="textSecondary" gutterBottom align="left">
                광고 또는 이벤트 소스를 입력하세요.
              </Typography>
              {/* <TextField fullWidth label="기타" variant="outlined" value={utmParams.source} onChange={(e) => handleChange(e, "source")} /> */}
            </Grid>
          </Grid>
        </Box>
        <Box mb={2}>
          <Grid container spacing={2}>
            <Grid item xs={5}>
              {/* <TextField label="Medium" variant="outlined" fullWidth value={utmParams.medium} onChange={(e) => handleChange(e, "medium")} /> */}
              <Autocomplete
                options={mediums}
                getOptionLabel={(option) => {
                  if (typeof option === "string") {
                    return option;
                  }
                  // Regular option
                  return "";
                }}
                filterOptions={(options, params) => {
                  const filtered = filter(options, params);

                  const { inputValue } = params;
                  // Suggest the creation of a new value
                  const isExisting = options.some((option) => inputValue === option);
                  if (inputValue !== "" && !isExisting) {
                    filtered.push(`Add "${inputValue}"`); //inputValue,
                  }

                  return filtered;
                }}
                freeSolo
                selectOnFocus
                value={utmParams.medium}
                onChange={(e, newValue) => handleChangeAutoComplete(newValue, "medium")}
                renderInput={(params) => (
                  <div>
                    {" "}
                    <TextField {...params} required focused color="secondary" label="Medium" variant="outlined" fullWidth />{" "}
                  </div>
                )}
              />
            </Grid>
            <Grid item xs={7}>
              <Typography variant="body1" color="textSecondary" gutterBottom align="left">
                링크가 게시되는 매체의 종류
              </Typography>
            </Grid>
          </Grid>
        </Box>
        <Box mb={2}>
          <Grid container spacing={2}>
            <Grid item xs={5}>
              <TextField required focused color="secondary" label="Campaign" variant="outlined" fullWidth value={utmParams.campaign} onChange={(e) => handleChange(e, "campaign")} />
            </Grid>
            <Grid item xs={7}>
              <Typography variant="body1" color="textSecondary" gutterBottom align="left">
                한글로 된 캠페인 이름 <br /> ex. 가을신상, 여름대전, ....
              </Typography>
            </Grid>
          </Grid>
        </Box>
        <Box mb={2}>
          <Grid container spacing={2}>
            <Grid item xs={5}>
              <TextField required focused color="secondary" label="Content" variant="outlined" fullWidth value={utmParams.content} onChange={(e) => handleChange(e, "content")} />
            </Grid>
            <Grid item xs={7}>
              <Typography variant="body1" color="textSecondary" gutterBottom align="left">
                타게팅하는 고객군 이름, 실험명, 블로거아이디, 카페아이디 등<br />
                ex. 20대, 30대, 하남, 광주, yeonjin8903, ysolmom
              </Typography>
            </Grid>
          </Grid>
        </Box>
        <Box mb={2}>
          <Grid container spacing={2}>
            <Grid item xs={5}>
              <TextField label="Term (optional)" variant="outlined" fullWidth value={utmParams.term} onChange={(e) => handleChange(e, "term")} />
            </Grid>
            <Grid item xs={7}>
              <Typography variant="body1" color="textSecondary" gutterBottom align="left">
                광고 컨텐츠의 키워드- 해시태그, SEO키워드, 광고키워드 등 (수동)
                <br />
                (블로그등의 게시글일 경우 컨텐츠 입력하여 자동 생성)
              </Typography>
            </Grid>
          </Grid>
        </Box>

        <Box mb={2}>
          <Button variant="contained" color="primary" onClick={generateUTM}>
            생성
          </Button>
        </Box>
        {generatedUrl && (
          <Box>
            <Typography variant="h6">생성된 UTM 링크</Typography>
            <TextField
              variant="outlined"
              fullWidth
              value={generatedUrl}
              InputProps={{
                readOnly: true,
              }}
            />
            <Box mt={2}>
              <Button
                variant="contained"
                color="secondary"
                onClick={() => {
                  navigator.clipboard.writeText(generatedUrl);
                }}
              >
                복사
              </Button>
            </Box>
          </Box>
        )}
        {/* <EditableAutoSizedTable tableName="utm_data" authToken={authToken} burl={burl} createdId=/> */}
        <EditableAutoSizedTable client={api} createdId={rowId} />
        <Dialog open={openDialog} onClose={handleCloseDialog}>
          <DialogTitle>Missing Fields</DialogTitle>
          <DialogContent>
            <DialogContentText>
              다음의 필드들은 필수 값입니다.
              <ul>
                {missingFields.map((field) => (
                  <li key={field}>{field}</li>
                ))}
              </ul>
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog} color="primary">
              OK
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </React.Fragment>
  );
};

export default UTMGenerator;
